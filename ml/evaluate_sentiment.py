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

from ml.labels import SENTIMENT_LABELS


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


def main(argv: list[str] | None = None) -> None:
    from ml.data import load_dataset

    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--pipeline", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)

    pipeline_path = Path(args.pipeline)
    metadata = json.loads(
        (pipeline_path.parent / "sentiment_metadata.json").read_text(encoding="utf-8"))
    algorithm = metadata["algorithm"]
    pipeline = joblib.load(pipeline_path)
    test_frame = load_dataset(args.data_dir)["test"]

    result = evaluate_models({algorithm: pipeline}, test_frame)[algorithm]
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "selected_test.json").write_text(
        json.dumps({"algorithm": algorithm, "test": result},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out / 'selected_test.json'}")


if __name__ == "__main__":
    main()