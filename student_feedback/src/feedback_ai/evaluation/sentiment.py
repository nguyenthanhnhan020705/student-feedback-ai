"""Đánh giá mô hình cảm xúc (không fit, không chọn lại winner)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import (accuracy_score, confusion_matrix,
                             precision_recall_fscore_support)

from feedback_ai.common.labels import SENTIMENT_LABELS


def compute_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    labels = list(SENTIMENT_LABELS)
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0)
    mp, mr, mf, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_precision": float(mp),
        "macro_recall": float(mr),
        "macro_f1": float(mf),
        "per_class": [
            {"label": lb, "precision": float(p[i]), "recall": float(r[i]),
             "f1": float(f[i]), "support": int(s[i])}
            for i, lb in enumerate(labels)
        ],
        "confusion_matrix": cm.astype(int).tolist(),  # hàng=thật, cột=dự đoán
        "label_order": labels,
        "n_rows": int(len(y_true)),
    }


def evaluate_models(models: dict[str, Any], frame: pd.DataFrame) -> dict[str, Any]:
    texts = frame["text"].tolist()
    y_true = frame["sentiment"].tolist()
    return {name: compute_metrics(y_true, [str(x) for x in pipe.predict(texts)])
            for name, pipe in models.items()}


