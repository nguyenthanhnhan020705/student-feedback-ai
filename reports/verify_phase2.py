"""Verify frozen Data/ML handoff without fitting or rewriting baseline evidence.

Run with the Phase 1 locked environment. Only phase-2 evidence is written.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from importlib.metadata import version

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import joblib
import nbformat
from ml.data import inspect_data, load_dataset
from ml.preprocessing import normalize_text
from ml.evaluate_sentiment import evaluate_models as evaluate_sentiment
from ml.evaluate_topic import evaluate_models as evaluate_topic


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_task(task):
    """Executed in a fresh interpreter separately for each trusted artifact."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import LinearSVC
    from ml.labels import SENTIMENT_LABELS, TOPIC_LABELS

    labels = list(SENTIMENT_LABELS if task == "sentiment" else TOPIC_LABELS)
    metadata = read(f"models/{task}_metadata.json")
    comparison = read(f"reports/metrics/{task}/comparison.json")
    selected = read(f"reports/metrics/{task}/selected_test.json")
    reload = read(f"reports/evidence/{task}/reload.json")
    artifact = ROOT / "models" / metadata["artifact_filename"]
    assert digest(artifact) == metadata["artifact_sha256"] == reload["artifact_sha256"]
    assert metadata["dataset_manifest_sha256"] == comparison["dataset_manifest_sha256"] == digest(ROOT / "reports/data/manifest.json")
    assert platform.python_version_tuple()[:2] == ("3", "13")
    assert metadata["python_version"].split(".")[:2] == ["3", "13"]
    runtime = {name: version(name) for name in ("numpy", "scipy", "pandas", "scikit-learn", "joblib")}
    assert runtime == metadata["package_versions"]
    assert metadata["labels"] == labels
    assert metadata["selection"] == comparison["selection"]
    # Compare all three frozen configurations with code without training them.
    if task == "sentiment":
        from ml.train_sentiment import TFIDF_PARAMS, CLF_PARAMS
        current_config = dict(tfidf=TFIDF_PARAMS, classifiers=CLF_PARAMS)
    else:
        from ml.train_topic import build_pipeline, pipeline_parameters
        current_config = {key: pipeline_parameters(build_pipeline(key))
                          for key in ("nb", "logistic_regression", "linear_svm")}
    assert json.loads(json.dumps(current_config)) == comparison["configuration"]
    winner = metadata["algorithm"]
    assert winner == selected["algorithm"] == "linear_svm"
    assert comparison["selection"]["metric"] == "macro_f1"
    assert comparison["selection"]["validation_metrics"] == comparison["validation"][winner]
    for split in ("validation", "test"):
        assert set(comparison[split]) == {"nb", "logistic_regression", "linear_svm"}
        for metrics in comparison[split].values():
            assert metrics["label_order"] == labels
            assert metrics["n_rows"] == (1583 if split == "validation" else 3166)
            assert sum(map(sum, metrics["confusion_matrix"])) == metrics["n_rows"]
    assert winner == max(comparison["validation"], key=lambda name: comparison["validation"][name]["macro_f1"])
    pipeline = joblib.load(artifact)
    tfidf, classifier = pipeline.steps[0][1], pipeline.steps[1][1]
    assert isinstance(tfidf, TfidfVectorizer) and isinstance(classifier, LinearSVC)
    assert set(pipeline.classes_) == set(labels)
    assert tfidf.preprocessor is normalize_text
    expected_tfidf = dict(ngram_range=(1, 2), min_df=2, max_df=1.0, sublinear_tf=True,
                          norm="l2", strip_accents=None, lowercase=False, token_pattern=r"(?u)\b\w+\b")
    for key, value in expected_tfidf.items():
        assert getattr(tfidf, key) == value, (task, key)
        saved = metadata["parameters"]["tfidf"][key]
        assert saved == (list(value) if isinstance(value, tuple) else value)
    for key, value in dict(C=1.0, dual="auto", max_iter=5000, class_weight=None, random_state=42).items():
        assert getattr(classifier, key) == value
        assert metadata["parameters"]["classifier"][key] == value
    frames = load_dataset(ROOT / "data/raw")
    evaluator = evaluate_sentiment if task == "sentiment" else evaluate_topic
    recomputed = {}
    for split in ("validation", "test"):
        recomputed[split] = evaluator({winner: pipeline}, frames[split])[winner]
        assert recomputed[split] == comparison[split][winner], (task, split, "metrics differ")
    assert recomputed["test"] == selected["test"]
    predictions = [str(label) for label in pipeline.predict(reload["samples"])]
    assert predictions == reload["before"] == reload["after_new_process"]
    errors = read(f"reports/metrics/{task}/error_analysis.json")
    actual = pipeline.predict(frames["test"].text.tolist())
    assert errors["errors"] == sum(a != b for a, b in zip(actual, frames["test"][task]))
    # Reconstruct train-only vocabulary/IDF independently; never call fit.
    import numpy as np
    from collections import Counter
    counts = Counter()
    analyzer = tfidf.build_analyzer()
    for text in frames["train"].text:
        counts.update(set(analyzer(text)))
    expected_terms = {term for term, count in counts.items() if count >= 2}
    assert set(tfidf.vocabulary_) == expected_terms
    expected_idf = np.empty(len(tfidf.vocabulary_))
    for term, index in tfidf.vocabulary_.items():
        expected_idf[index] = np.log((1 + len(frames["train"])) / (1 + counts[term])) + 1
    np.testing.assert_allclose(tfidf.idf_, expected_idf, rtol=0, atol=1e-12)
    return dict(task=task, algorithm=winner, artifact_sha256=digest(artifact), runtime=runtime,
                manifest_sha256=metadata["dataset_manifest_sha256"], metrics=recomputed,
                reload_predictions=predictions, vocabulary_size=len(expected_terms),
                train_only_vocabulary_and_idf=True, errors=errors["errors"], pid=os.getpid())


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--task":
        print(json.dumps(verify_task(sys.argv[2]), ensure_ascii=False))
        return
    protected = [path for directory in ("ml", "models", "data", "notebooks", "reports/data", "reports/metrics", "reports/figures")
                 for path in (ROOT / directory).rglob("*") if path.is_file() and "__pycache__" not in path.parts]
    before = {str(path.relative_to(ROOT)): digest(path) for path in protected}
    source, manifest = read("reports/data/source.json"), read("reports/data/manifest.json")
    assert inspect_data(ROOT / "data/raw", source=source) == manifest
    assert {name: item["rows"] for name, item in manifest["splits"].items()} == dict(train=11426, validation=1583, test=3166)
    assert len(source["files"]) == 9
    for item in source["files"]:
        assert digest(ROOT / "data/raw" / item["path"]) == item["sha256"]
    notebooks = []
    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        cells = [cell for cell in nb.cells if cell.cell_type == "code"]
        assert cells and all(cell.execution_count is not None for cell in cells)
        assert not any(output.output_type == "error" for cell in cells for output in cell.outputs)
        if path.name in ("02_sentiment.ipynb", "03_topic.ipynb"):
            task = "sentiment" if path.name.startswith("02") else "topic"
            comparison = read(f"reports/metrics/{task}/comparison.json")
            output_text = "\n".join(output.get("text", "") for cell in cells
                                    for output in cell.outputs if output.output_type == "stream")
            for split in ("validation", "test"):
                for algorithm, metrics in comparison[split].items():
                    lines = [line for line in output_text.splitlines()
                             if line.replace("|", " ").split()[:2] == [split, algorithm]]
                    assert len(lines) == 1, (path.name, split, algorithm)
                    values = [metrics[key] for key in ("accuracy", "macro_precision", "macro_recall", "macro_f1")]
                    recorded = [float(token) for token in lines[0].replace("|", " ").split()[-4:]]
                    assert recorded == [round(value, 6) for value in values]
        notebooks.append(dict(path=str(path.relative_to(ROOT)), code_cells=len(cells),
                              executions=[cell.execution_count for cell in cells], errors=0,
                              method="schema and stored-output inspection; no training cells rerun"))
    tasks = []
    for task in ("sentiment", "topic"):
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--task", task],
                                   cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
                                   env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"})
        tasks.append(json.loads(completed.stdout))
    assert all(digest(ROOT / path) == value for path, value in before.items()), "Frozen inputs changed"
    result = dict(python=platform.python_version(), executable=sys.executable,
                  rows={name: item["rows"] for name, item in manifest["splits"].items()},
                  duplicates=manifest["duplicates"], notebooks=notebooks, tasks=tasks,
                  protected_hashes=before, protected_files_unchanged=True,
                  scope="No fit; non-winning models checked against stored evidence, not retrained.")
    target = ROOT / "reports/evidence/phase-2/verification.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(rows=result["rows"], tasks=[t["task"] for t in tasks],
                         protected_files=len(before), unchanged=True)))


if __name__ == "__main__":
    main()
