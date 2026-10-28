"""Topic model inference and trusted-artifact verification (contract v1.0).

The model receives RAW strings, calls ml.preprocessing.normalize_text inside
the persisted TF-IDF pipeline, and returns canonical string Topic labels.
Only load joblib artifacts received from trusted project members.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import joblib
import numpy
import pandas
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


MODEL_CLASSES = {
    "nb": MultinomialNB,
    "logistic_regression": LogisticRegression,
    "linear_svm": LinearSVC,
}
REQUIRED_METADATA = {
    "contract_version", "task", "algorithm", "artifact_filename",
    "artifact_sha256", "labels", "python_version", "package_versions",
    "dataset_manifest_sha256", "preprocessing", "parameters", "selection", "trained_at",
}


def predict_texts(pipeline: Pipeline, texts: list[str]) -> list[str]:
    """Return canonical labels in input order; [] -> [].

    Do NOT apply the web/API 5000-code-point limit to corpus/model inference.
    Input normalization is already built into the trained pipeline.
    """
    if not isinstance(texts, list):
        raise ValueError("texts must be a list of raw strings")
    if not texts:
        return []
    if any(not isinstance(value, str) or not value.strip() for value in texts):
        raise ValueError("Every Topic text must be a nonblank string")
    return [str(value) for value in pipeline.predict(texts)]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _runtime_versions() -> dict[str, str]:
    return {
        "numpy": numpy.__version__, "scipy": scipy.__version__,
        "pandas": pandas.__version__, "scikit-learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }


def load_topic_pipeline(
    pipeline_path: str | Path,
    metadata_path: str | Path,
) -> tuple[Pipeline, dict]:
    """Verify v1.0 schema, labels, SHA-256, environment, and model structure."""
    from ml.labels import TOPIC_LABELS
    from ml.preprocessing import normalize_text

    artifact = Path(pipeline_path)
    metadata_file = Path(metadata_path)
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict) or not REQUIRED_METADATA.issubset(metadata):
        raise ValueError("Topic metadata is not compliant with contract v1.0")
    if metadata["contract_version"] != "1.0" or metadata["task"] != "topic":
        raise ValueError("Incorrect contract version or task")
    algorithm = metadata["algorithm"]
    if algorithm not in MODEL_CLASSES:
        raise ValueError("Invalid Topic algorithm in metadata")
    if metadata["artifact_filename"] != "topic_pipeline.joblib" or artifact.name != metadata["artifact_filename"]:
        raise ValueError("Incorrect Topic artifact filename")
    if (metadata["labels"] != list(TOPIC_LABELS) or
            tuple(TOPIC_LABELS) != ("lecturer", "curriculum", "facility", "other")):
        raise ValueError("Topic labels differ from the canonical Data labels")
    if (not isinstance(metadata["artifact_sha256"], str) or
            re.fullmatch(r"[0-9a-f]{64}", metadata["artifact_sha256"]) is None or
            _sha256_file(artifact) != metadata["artifact_sha256"]):
        raise ValueError("Topic model checksum mismatch")
    if (not isinstance(metadata["dataset_manifest_sha256"], str) or
            re.fullmatch(r"[0-9a-f]{64}", metadata["dataset_manifest_sha256"]) is None):
        raise ValueError("Invalid dataset manifest SHA-256 in metadata")
    if metadata["preprocessing"] != {"name": "ml.preprocessing.normalize_text", "version": "1.0"}:
        raise ValueError("Unknown Topic preprocessing contract")
    if (not isinstance(metadata["selection"], dict) or
            metadata["selection"].get("algorithm") != algorithm or
            metadata["selection"].get("metric") != "macro_f1"):
        raise ValueError("Topic selection does not match the artifact")
    if (not isinstance(metadata["parameters"], dict) or
            not isinstance(metadata["trained_at"], str)):
        raise ValueError("Incomplete model parameters or timestamp")

    trained_python = str(metadata["python_version"])
    if (not trained_python.startswith("3.13.") or
            sys.version_info[:2] != (3, 13)):
        raise ValueError("Topic artifacts require matching CPython 3.13.x environments")
    if metadata["package_versions"] != _runtime_versions():
        raise ValueError("Package versions differ from the model training environment")

    pipeline = joblib.load(artifact)  # SECURITY: only from trusted local sources.
    if (not isinstance(pipeline, Pipeline) or
            list(pipeline.named_steps) != ["tfidf", "classifier"] or
            not isinstance(pipeline.named_steps["tfidf"], TfidfVectorizer) or
            not isinstance(pipeline.named_steps["classifier"], MODEL_CLASSES[algorithm])):
        raise ValueError("Topic artifact has the wrong pipeline structure")
    vectorizer = pipeline.named_steps["tfidf"]
    if (vectorizer.preprocessor is not normalize_text or
            vectorizer.lowercase is not False or vectorizer.min_df != 2):
        raise ValueError("Topic pipeline uses an unexpected text preprocessor")
    model_classes = getattr(pipeline, "classes_", None)
    if model_classes is None or set(model_classes) != set(TOPIC_LABELS):
        raise ValueError("Fitted Topic model classes differ from canonical labels")
    return pipeline, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict using a verified Topic artifact")
    parser.add_argument("--pipeline", default="models/topic_pipeline.joblib")
    parser.add_argument("--metadata", default="models/topic_metadata.json")
    parser.add_argument("--text", required=True, action="append", help="May be repeated")
    args = parser.parse_args()
    pipeline, _ = load_topic_pipeline(args.pipeline, args.metadata)
    print(json.dumps(
        predict_texts(pipeline, args.text), ensure_ascii=False, indent=2
    ))


if __name__ == "__main__":
    main()
