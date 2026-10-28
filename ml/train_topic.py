"""Train the contract-v1.0 Topic baseline on UIT-VSFC canonical splits.

CLI: python -m ml.train_topic --data-dir data/raw --output-dir models \
     --report-dir reports/metrics/topic

Data owns ml.data/ml.preprocessing/ml.labels; this module imports their
interfaces and never remaps labels, changes splits, or performs extra cleanup.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
from typing import Any

import joblib
import numpy
import pandas as pd
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from ml.evaluate_topic import (
    MODEL_KEYS,
    evaluate_models,
    save_confusion_figure,
    topic_labels,
    validate_topic_frame,
)


def build_pipeline(algorithm: str) -> Pipeline:
    """Create EXACT TF-IDF/classifier baseline from contract section 5."""
    from ml.preprocessing import normalize_text

    classifiers = {
        "nb": MultinomialNB(alpha=1.0),
        "logistic_regression": LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=2000, class_weight=None,
            random_state=42,
        ),
        "linear_svm": LinearSVC(
            C=1.0, dual="auto", max_iter=5000, class_weight=None,
            random_state=42,
        ),
    }
    if algorithm not in classifiers:
        raise ValueError(f"Unknown Topic algorithm {algorithm!r}")
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2), min_df=2, max_df=1.0,
            sublinear_tf=True, norm="l2", strip_accents=None,
            lowercase=False, preprocessor=normalize_text,
            token_pattern=r"(?u)\b\w+\b",
        )),
        ("classifier", classifiers[algorithm]),
    ])


def train_models(train_frame: pd.DataFrame) -> dict[str, Pipeline]:
    """Fit all three independent pipelines on TRAIN raw sentences only."""
    validate_topic_frame(train_frame, split="train")
    if set(train_frame["topic"]) != set(topic_labels()):
        raise ValueError("TRAIN must contain all four canonical Topic classes")
    x_train = train_frame["text"].tolist()
    y_train = train_frame["topic"].tolist()
    models: dict[str, Pipeline] = {}
    for algorithm in MODEL_KEYS:
        model = build_pipeline(algorithm)
        model.fit(x_train, y_train)
        models[algorithm] = model
    return models


def select_model(
    models: dict[str, Pipeline], validation_frame: pd.DataFrame
) -> dict[str, Any]:
    """Freeze a winner by validation macro-F1; never inspect the test split.

    Differences <= 0.000001 are ties. Break them with validation accuracy,
    then fixed nb -> logistic_regression -> linear_svm order.
    """
    validate_topic_frame(validation_frame, split="validation")
    results = evaluate_models(models, validation_frame)
    if not results:
        raise ValueError("No models to compare")
    tolerance = 0.000001
    winner: str | None = None
    for candidate in MODEL_KEYS:
        if candidate not in results:
            continue
        if winner is None:
            winner = candidate
            continue
        a, b = results[candidate], results[winner]
        if a["macro_f1"] > b["macro_f1"] + tolerance:
            winner = candidate
        elif abs(a["macro_f1"] - b["macro_f1"]) <= tolerance:
            if a["accuracy"] > b["accuracy"] + tolerance:
                winner = candidate
    assert winner is not None
    return {
        "algorithm": winner,
        "metric": "macro_f1",
        "validation_metrics": results[winner],
    }


def pipeline_parameters(pipeline: Pipeline) -> dict[str, Any]:
    """Serialize effective TF-IDF and classifier parameter values."""
    tfidf = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["classifier"]
    vectorizer = {
        "ngram_range": list(tfidf.ngram_range),
        "min_df": tfidf.min_df,
        "max_df": tfidf.max_df,
        "sublinear_tf": tfidf.sublinear_tf,
        "norm": tfidf.norm,
        "strip_accents": tfidf.strip_accents,
        "lowercase": tfidf.lowercase,
        "preprocessor": "ml.preprocessing.normalize_text",
        "token_pattern": tfidf.token_pattern,
    }
    if isinstance(classifier, MultinomialNB):
        params = {"alpha": classifier.alpha}
    elif isinstance(classifier, LogisticRegression):
        params = {
            "C": classifier.C, "solver": classifier.solver,
            "max_iter": classifier.max_iter,
            "class_weight": classifier.class_weight,
            "random_state": classifier.random_state,
        }
    elif isinstance(classifier, LinearSVC):
        params = {
            "C": classifier.C, "dual": classifier.dual,
            "max_iter": classifier.max_iter,
            "class_weight": classifier.class_weight,
            "random_state": classifier.random_state,
        }
    else:
        raise ValueError("Unexpected classifier in Topic pipeline")
    return {"tfidf": vectorizer, "classifier": {"name": type(classifier).__name__, **params}}


def package_versions() -> dict[str, str]:
    return {
        "numpy": numpy.__version__, "scipy": scipy.__version__,
        "pandas": pd.__version__, "scikit-learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }


def sha256_file(path: str | Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_training_results(
    models: dict[str, Pipeline],
    selection: dict[str, Any],
    validation: dict[str, Any],
    test: dict[str, Any],
    *,
    manifest_sha256: str,
    output_dir: str | Path,
    report_dir: str | Path,
) -> dict[str, Path]:
    """Save real, computed results; refuse to overwrite prior evidence."""
    winner = selection["algorithm"]
    if winner not in models or len(manifest_sha256) != 64:
        raise ValueError("Missing winner or dataset manifest SHA-256")
    output = Path(output_dir)
    reports = Path(report_dir)
    pipeline_path = output / "topic_pipeline.joblib"
    metadata_path = output / "topic_metadata.json"
    comparison_path = reports / "comparison.json"
    figure_path = Path(__file__).resolve().parents[1] / "reports/figures/topic/confusion_matrix.png"
    for path in (pipeline_path, metadata_path, comparison_path, figure_path):
        if path.exists():
            raise FileExistsError(f"Refusing to replace an existing artifact/report: {path}")
    output.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    configuration = {algorithm: pipeline_parameters(model) for algorithm, model in models.items()}
    comparison = {
        "contract_version": "1.0", "task": "topic",
        "dataset_manifest_sha256": manifest_sha256,
        "configuration": configuration, "selection": selection,
        "validation": validation, "test": test,
    }
    joblib.dump(models[winner], pipeline_path)
    metadata = {
        "contract_version": "1.0", "task": "topic", "algorithm": winner,
        "artifact_filename": pipeline_path.name,
        "artifact_sha256": sha256_file(pipeline_path),
        "labels": list(topic_labels()),
        "python_version": platform.python_version(),
        "package_versions": package_versions(),
        "dataset_manifest_sha256": manifest_sha256,
        "preprocessing": {"name": "ml.preprocessing.normalize_text", "version": "1.0"},
        "parameters": configuration[winner], "selection": selection,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    comparison_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    save_confusion_figure(test[winner], figure_path)
    return {"pipeline": pipeline_path, "metadata": metadata_path,
            "comparison": comparison_path, "confusion_figure": figure_path}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the Topic v1.0 baseline")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--output-dir", default="models")
    parser.add_argument("--report-dir", default="reports/metrics/topic")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 13):
        parser.error("Contract v1.0 requires CPython 3.13.x, 64-bit; select the project .venv")
    if platform.architecture()[0] != "64bit":
        parser.error("Contract v1.0 requires 64-bit Python")

    from ml.data import load_dataset

    manifest_path = Path(__file__).resolve().parents[1] / "reports/data/manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError("M1 dataset manifest is missing: " + str(manifest_path))
    manifest_hash = sha256_file(manifest_path)
    frames = load_dataset(args.data_dir)
    if set(frames) != {"train", "validation", "test"}:
        raise ValueError("Data loader must return train/validation/test")
    for name in ("train", "validation", "test"):
        validate_topic_frame(frames[name], split=name)

    models = train_models(frames["train"])
    selection = select_model(models, frames["validation"])
    # Winner and hyperparameters are frozen BEFORE the one-time test evaluation.
    validation = evaluate_models(models, frames["validation"])
    test = evaluate_models(models, frames["test"])
    paths = save_training_results(
        models, selection, validation, test,
        manifest_sha256=manifest_hash,
        output_dir=args.output_dir, report_dir=args.report_dir,
    )
    print(f"Selected on validation: {selection['algorithm']}")
    for role, path in paths.items():
        print(f"{role}: {path}")


if __name__ == "__main__":
    main()
