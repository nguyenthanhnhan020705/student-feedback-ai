"""Topic metrics and test-only verification, per Data/model contract v1.0.

CLI: python -m feedback_ai.evaluation.topic --data-dir data/raw \
     --pipeline models/topic_pipeline.joblib --output-dir reports/metrics/topic
No fitting, model selection, or modification of comparison.json happens here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import Pipeline

MODEL_KEYS = ("nb", "logistic_regression", "linear_svm")
EXPECTED_COLUMNS = ("id", "text", "sentiment", "topic", "split")
VALID_SPLITS = {"train", "validation", "test"}


def verify_dataset_manifest(data_dir: str | Path, manifest_path: str | Path) -> str:
    """Bind metrics to actual source bytes, not just an unrelated manifest file."""
    import hashlib
    from feedback_ai.data.loader import inspect_data

    payload = Path(manifest_path).read_bytes()
    manifest = json.loads(payload)
    actual = inspect_data(data_dir)
    for key in ('schema_version', 'splits', 'duplicates', 'policy'):
        if manifest.get(key) != actual[key]:
            raise ValueError(f'Dataset manifest mismatch: {key}')
    return hashlib.sha256(payload).hexdigest()


def topic_labels() -> tuple[str, ...]:
    """Retrieve the canonical labels from Data; never remap them locally."""
    from feedback_ai.common.labels import TOPIC_LABELS

    labels = tuple(TOPIC_LABELS)
    if labels != ("lecturer", "curriculum", "facility", "other"):
        raise ValueError("feedback_ai.common.labels.TOPIC_LABELS differs from Data/model v1.0")
    return labels


def validate_topic_frame(frame: pd.DataFrame, *, split: str | None = None) -> None:
    """Check the Data loader's five-column contract without changing rows."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame from feedback_ai.data.loader")
    if tuple(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"Expected columns, in order: {EXPECTED_COLUMNS}")
    if frame.empty:
        raise ValueError("Evaluation/training frame must not be empty")
    for column in EXPECTED_COLUMNS:
        if any(not isinstance(item, str) for item in frame[column]):
            raise ValueError(f"Column {column} must contain non-null Python strings")
    if any(not text.strip() for text in frame["text"]):
        raise ValueError("Blank text is not allowed")
    splits = set(frame["split"])
    if len(splits) != 1 or not splits.issubset(VALID_SPLITS):
        raise ValueError("DataFrame must contain one valid, unmixed split")
    if split is not None and splits != {split}:
        raise ValueError(f"Expected {split!r} split, got {sorted(splits)}")
    if not set(frame["topic"]).issubset(topic_labels()):
        raise ValueError("Unknown Topic labels; verify Data's canonical mapping")


def metrics_for_predictions(
    y_true: list[str], y_pred: list[str]
) -> dict[str, Any]:
    """Return EXACT metric keys in section 6 of the v1.0 contract."""
    labels = topic_labels()
    if len(y_true) == 0 or len(y_true) != len(y_pred):
        raise ValueError("Expected nonempty, aligned true/predicted labels")
    if not set(y_true).issubset(labels) or not set(y_pred).issubset(labels):
        raise ValueError("Predicted/true Topic label is outside canonical labels")

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average=None, zero_division=0
    )
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_precision": float(macro_p),
        "macro_recall": float(macro_r),
        "macro_f1": float(macro_f1),
        "per_class": [
            {
                "label": label,
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, label in enumerate(labels)
        ],
        "confusion_matrix": cm.astype(int).tolist(),
        "label_order": list(labels),
        "n_rows": len(y_true),
    }


def evaluate_models(
    models: dict[str, Pipeline], frame: pd.DataFrame
) -> dict[str, Any]:
    """Score all supplied trained Topic models; never call fit or select."""
    validate_topic_frame(frame)
    if not models or any(key not in MODEL_KEYS for key in models):
        raise ValueError(f"Models must use these keys (or a subset): {MODEL_KEYS}")
    texts = frame["text"].tolist()  # Raw strings, not normalized twice.
    truths = frame["topic"].tolist()
    return {
        key: metrics_for_predictions(truths, list(model.predict(texts)))
        for key, model in models.items()
    }


def save_confusion_figure(metrics: dict[str, Any], path: str | Path) -> None:
    """Draw the winner's actual test confusion matrix after evaluation."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay

    target = Path(path)
    if target.exists():
        raise FileExistsError(f"Confusion figure already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    ConfusionMatrixDisplay(
        np.array(metrics["confusion_matrix"], dtype=int),
        display_labels=metrics["label_order"],
    ).plot(ax=ax, colorbar=False, xticks_rotation=30)
    fig.tight_layout()
    fig.savefig(target, dpi=180, bbox_inches="tight")
    plt.close(fig)


