"""Huấn luyện, chọn mô hình (validation) và xuất artifact cảm xúc."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from feedback_ai.evaluation.sentiment import evaluate_models
from feedback_ai.common.labels import SENTIMENT_LABELS
from feedback_ai.data.preprocessing import normalize_text

CONTRACT_VERSION = "1.0"
TFIDF_PARAMS: dict[str, Any] = dict(
    ngram_range=(1, 2), min_df=2, max_df=1.0, sublinear_tf=True, norm="l2",
    strip_accents=None, lowercase=False, token_pattern=r"(?u)\b\w+\b")
CLF_PARAMS: dict[str, dict[str, Any]] = {
    "nb": {"alpha": 1.0},
    "logistic_regression": {"C": 1.0, "solver": "lbfgs", "max_iter": 2000,
                            "class_weight": None, "random_state": 42},
    "linear_svm": {"C": 1.0, "dual": "auto", "max_iter": 5000,
                   "class_weight": None, "random_state": 42},
}
CLF_CLASSES = {"nb": MultinomialNB, "logistic_regression": LogisticRegression,
               "linear_svm": LinearSVC}
ORDER = ("nb", "logistic_regression", "linear_svm")
TOL = 1e-6


def _require_split(frame: pd.DataFrame, split: str) -> None:
    if not (frame["split"] == split).all():
        raise ValueError(f"Mọi dòng phải có split={split!r}")


def train_models(train_frame: pd.DataFrame) -> dict[str, Pipeline]:
    _require_split(train_frame, "train")
    if not train_frame["sentiment"].isin(SENTIMENT_LABELS).all():
        raise ValueError("Train sentiment labels must be canonical and non-null")
    missing = set(SENTIMENT_LABELS) - set(train_frame["sentiment"])
    if missing:
        raise ValueError(f"Tập train thiếu nhãn: {sorted(missing)}")
    texts = train_frame["text"].tolist()
    y = train_frame["sentiment"].tolist()
    models: dict[str, Pipeline] = {}
    for name in ORDER:
        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(preprocessor=normalize_text, **TFIDF_PARAMS)),
            ("clf", CLF_CLASSES[name](**CLF_PARAMS[name])),
        ])
        models[name] = pipe.fit(texts, y)
    return models


def select_model(models: dict[str, Pipeline],
                 validation_frame: pd.DataFrame) -> dict[str, Any]:
    _require_split(validation_frame, "validation")
    val = evaluate_models(models, validation_frame)
    best: str | None = None
    for name in ORDER:  # thứ tự cố định cũng là luật hòa cuối cùng
        if name not in val:
            continue
        if best is None:
            best = name
            continue
        m, b = val[name], val[best]
        if m["macro_f1"] > b["macro_f1"] + TOL:
            best = name
        elif (abs(m["macro_f1"] - b["macro_f1"]) <= TOL
              and m["accuracy"] > b["accuracy"] + TOL):
            best = name
    if best is None:
        raise ValueError("Không có mô hình để chọn")
    return {"algorithm": best, "metric": "macro_f1",
            "validation_metrics": val[best]}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def _save_confusion_matrix(metrics: dict[str, Any], path: Path, title: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = metrics["label_order"]
    cm = metrics["confusion_matrix"]
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels)), labels)
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("Dự đoán")
    ax.set_ylabel("Thực tế")
    ax.set_title(title)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, cm[i][j], ha="center", va="center")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


