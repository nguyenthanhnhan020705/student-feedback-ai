import hashlib
import json
import platform
from importlib.metadata import version

import joblib
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

from backend.model_service import ModelService


@pytest.fixture
def artifacts(tmp_path):
    # Synthetic training only: proves loading/serialization, not real model quality.
    for task, labels in [("sentiment", ["negative", "neutral", "positive"]), ("topic", ["lecturer", "curriculum", "facility", "other"])]:
        pipeline = make_pipeline(TfidfVectorizer(), MultinomialNB())
        pipeline.fit([f"sample token{i}" for i in range(len(labels))], labels)
        artifact = tmp_path / f"{task}_pipeline.joblib"
        joblib.dump(pipeline, artifact)
        metadata = {
            "contract_version": "1.0", "task": task, "algorithm": "nb",
            "artifact_filename": artifact.name,
            "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "labels": labels, "python_version": platform.python_version(),
            "package_versions": {name: version(name) for name in ["numpy", "scipy", "pandas", "scikit-learn", "joblib"]},
            "dataset_manifest_sha256": "a" * 64,
            "preprocessing": {"name": "ml.preprocessing.normalize_text", "version": "1.0"},
            "parameters": {"tfidf": {"ngram_range": [1, 1]}, "classifier": {"name": "nb", "alpha": 1.0}},
            "selection": {"algorithm": "nb", "metric": "macro_f1", "validation_metrics": {
                "accuracy": 1.0, "macro_precision": 1.0, "macro_recall": 1.0, "macro_f1": 1.0,
                "label_order": labels, "n_rows": len(labels),
                "per_class": [{"label": label, "precision": 1.0, "recall": 1.0,
                               "f1": 1.0, "support": 1} for label in labels],
                "confusion_matrix": [[int(i == j) for j in range(len(labels))]
                                     for i in range(len(labels))],
            }},
            "trained_at": "2026-10-28T00:00:00Z",
        }
        (tmp_path / f"{task}_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return tmp_path


def test_serialized_pipelines_match_direct_prediction_and_reload(artifacts):
    service = ModelService(artifacts)
    assert service.loaded
    result = service.predict("sample token0")
    for task in ["sentiment", "topic"]:
        assert result[task] == joblib.load(artifacts / f"{task}_pipeline.joblib").predict(["sample token0"])[0]
    (artifacts / "topic_metadata.json").unlink()
    service.reload()
    assert service.status == {"sentiment": "ready", "topic": "missing"}
    assert service.sentiment_model is None and service.topic_model is None
    with pytest.raises(RuntimeError):
        service.predict("sample")


@pytest.mark.parametrize("field,value", [
    ("contract_version", "2.0"), ("task", "topic"), ("algorithm", "unknown"),
    ("artifact_filename", "wrong.joblib"), ("artifact_sha256", "b" * 64),
    ("labels", ["positive"]), ("python_version", "3.12.1"),
    ("package_versions", {}), ("dataset_manifest_sha256", "invalid"),
    ("preprocessing", {}), ("parameters", []), ("selection", {}),
    ("trained_at", "2026-10-28T00:00:00"),
])
def test_incompatible_metadata_marks_only_affected_model_invalid(artifacts, field, value):
    path = artifacts / "sentiment_metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata[field] = value
    path.write_text(json.dumps(metadata), encoding="utf-8")
    service = ModelService(artifacts)
    assert service.status == {"sentiment": "invalid", "topic": "ready"}
    assert not service.loaded


@pytest.mark.parametrize("contents", ["{", "[]", "{}"])
def test_corrupt_metadata_does_not_prevent_startup(artifacts, contents):
    (artifacts / "sentiment_metadata.json").write_text(contents, encoding="utf-8")
    assert ModelService(artifacts).status == {"sentiment": "invalid", "topic": "ready"}


def test_corrupt_joblib_with_valid_checksum_is_invalid(artifacts):
    path = artifacts / "sentiment_pipeline.joblib"
    path.write_bytes(b"not a joblib artifact")
    meta_path = artifacts / "sentiment_metadata.json"
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    metadata["artifact_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    meta_path.write_text(json.dumps(metadata), encoding="utf-8")
    assert ModelService(artifacts).status["sentiment"] == "invalid"


def test_missing_models_do_not_prevent_startup(tmp_path):
    service = ModelService(tmp_path)
    assert service.status == {"sentiment": "missing", "topic": "missing"}
    assert not service.loaded


@pytest.mark.parametrize('field,value', [
    ('parameters', {}),
    ('parameters', {'tfidf': {}, 'classifier': {}}),
    ('selection', {'algorithm': 'nb', 'metric': 'macro_f1', 'validation_metrics': {}}),
    ('selection', {'algorithm': 'nb', 'metric': 'macro_f1', 'validation_metrics': {'accuracy': 2, 'macro_precision': 1, 'macro_recall': 1, 'macro_f1': 1}}),
])
def test_incomplete_nested_metadata_is_invalid(artifacts, field, value):
    path = artifacts / 'sentiment_metadata.json'
    metadata = json.loads(path.read_text(encoding='utf-8'))
    metadata[field] = value
    path.write_text(json.dumps(metadata), encoding='utf-8')
    assert ModelService(artifacts).status['sentiment'] == 'invalid'


def test_package_version_mismatch_is_invalid(artifacts):
    path = artifacts / "sentiment_metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["package_versions"]["scikit-learn"] = "0.0.0"
    path.write_text(json.dumps(metadata), encoding="utf-8")
    assert ModelService(artifacts).status["sentiment"] == "invalid"


def test_pipeline_classes_must_match_metadata(artifacts):
    artifact = artifacts / "sentiment_pipeline.joblib"
    pipeline = make_pipeline(TfidfVectorizer(), MultinomialNB())
    pipeline.fit(["alpha sample", "beta sample"], ["wrong", "labels"])
    joblib.dump(pipeline, artifact)
    path = artifacts / "sentiment_metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    path.write_text(json.dumps(metadata), encoding="utf-8")
    assert ModelService(artifacts).status["sentiment"] == "invalid"


@pytest.mark.parametrize("output", [[], ["positive", "negative"], ["unknown"], [None]])
def test_invalid_inference_output_is_rejected(artifacts, output):
    service = ModelService(artifacts)
    class BrokenPipeline:
        def predict(self, texts):
            return output
    service.sentiment_model = BrokenPipeline()
    with pytest.raises(ValueError):
        service.predict("sample")


@pytest.mark.parametrize("task", ["sentiment", "topic"])
@pytest.mark.parametrize("path,value", [
    (("python_version",), "3.13"),
    (("python_version",), "3.13.garbage"),
    (("python_version",), "3.13.3.extra"),
    (("selection", "validation_metrics", "per_class"), None),
    (("selection", "validation_metrics", "confusion_matrix"), []),
    (("selection", "validation_metrics", "label_order"), []),
    (("selection", "validation_metrics", "n_rows"), True),
    (("selection", "validation_metrics", "n_rows"), -1),
    (("selection", "validation_metrics", "n_rows"), 999),
    (("selection", "validation_metrics", "per_class", 0, "precision"), float("nan")),
    (("selection", "validation_metrics", "per_class", 0, "recall"), 2),
    (("selection", "validation_metrics", "per_class", 0, "f1"), "1"),
    (("selection", "validation_metrics", "per_class", 0, "support"), True),
    (("selection", "validation_metrics", "per_class", 0, "label"), "unknown"),
    (("selection", "validation_metrics", "confusion_matrix", 0), [1]),
    (("selection", "validation_metrics", "confusion_matrix", 0, 0), -1),
    (("selection", "validation_metrics", "confusion_matrix", 0, 0), True),
    (("selection", "validation_metrics", "confusion_matrix", 0, 0), 2),
])
def test_malformed_handoff_metadata_is_invalid(artifacts, task, path, value):
    metadata_path = artifacts / f"{task}_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    target = metadata
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    service = ModelService(artifacts)
    assert service.status[task] == "invalid"
    assert not service.loaded
    assert service.sentiment_model is None and service.topic_model is None


@pytest.mark.parametrize("task", ["sentiment", "topic"])
def test_metadata_labels_require_canonical_order(artifacts, task):
    path = artifacts / f"{task}_metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["labels"].reverse()
    path.write_text(json.dumps(metadata), encoding="utf-8")
    assert ModelService(artifacts).status[task] == "invalid"


def test_pipeline_class_order_may_differ_from_canonical_metadata(artifacts):
    # sklearn sorts topic classes alphabetically; metadata keeps the contract order.
    service = ModelService(artifacts)
    assert list(service.topic_model.classes_) == ["curriculum", "facility", "lecturer", "other"]
    assert service.loaded
