"""Unit test với FIXTURE nhỏ tự tạo. Không dùng làm kết quả nghiên cứu."""
import pandas as pd
import pytest

from ml.evaluate_sentiment import compute_metrics, evaluate_models
from ml.labels import SENTIMENT_LABELS
from ml.train_sentiment import ORDER, select_model, train_models

BASE = {
    "negative": ["giảng viên dạy rất tệ", "phòng học quá nóng và bẩn",
                 "môn học nhàm chán và khó hiểu"],
    "neutral": ["lớp học diễn ra vào buổi sáng", "môn học có bốn tín chỉ",
                "giảng viên phát tài liệu đầu giờ"],
    "positive": ["giảng viên dạy rất hay", "phòng học sạch sẽ và thoáng mát",
                 "môn học thú vị và dễ hiểu"],
}
COLUMNS = ["id", "text", "sentiment", "topic", "split"]


def make_frame(split: str, repeat: int = 4) -> pd.DataFrame:
    rows, n = [], 0
    for label, sentences in BASE.items():
        for _ in range(repeat):
            for s in sentences:
                n += 1
                rows.append({"id": f"{split}:{n:06d}", "text": s,
                             "sentiment": label, "topic": "other", "split": split})
    return pd.DataFrame(rows, columns=COLUMNS)


def test_train_returns_three_models():
    models = train_models(make_frame("train"))
    assert tuple(models) == ORDER


def test_train_rejects_wrong_split():
    with pytest.raises(ValueError):
        train_models(make_frame("validation"))


def test_train_rejects_missing_label():
    frame = make_frame("train")
    frame = frame[frame["sentiment"] != "neutral"]
    with pytest.raises(ValueError):
        train_models(frame)


def test_select_rejects_wrong_split():
    models = train_models(make_frame("train"))
    with pytest.raises(ValueError):
        select_model(models, make_frame("test"))


def test_select_tie_prefers_fixed_order(monkeypatch):
    fake = {"macro_f1": 0.5, "accuracy": 0.5}
    monkeypatch.setattr("ml.train_sentiment.evaluate_models",
                        lambda models, frame: {k: dict(fake) for k in models})
    result = select_model({k: None for k in ORDER}, make_frame("validation"))
    assert result["algorithm"] == "nb"


def test_select_prefers_higher_macro_f1(monkeypatch):
    scores = {"nb": 0.5, "logistic_regression": 0.7, "linear_svm": 0.6}
    monkeypatch.setattr(
        "ml.train_sentiment.evaluate_models",
        lambda models, frame: {k: {"macro_f1": scores[k], "accuracy": 0.5}
                               for k in models})
    result = select_model({k: None for k in ORDER}, make_frame("validation"))
    assert result["algorithm"] == "logistic_regression"
    assert result["metric"] == "macro_f1"


def test_metrics_structure():
    m = compute_metrics(["negative", "neutral", "positive", "positive"],
                        ["negative", "positive", "positive", "positive"])
    assert m["label_order"] == list(SENTIMENT_LABELS)
    assert m["n_rows"] == 4
    assert all(0.0 <= m[k] <= 1.0 for k in
               ("accuracy", "macro_precision", "macro_recall", "macro_f1"))
    assert len(m["confusion_matrix"]) == 3
    assert all(isinstance(v, int) and v >= 0 for row in m["confusion_matrix"] for v in row)
    assert [c["label"] for c in m["per_class"]] == list(SENTIMENT_LABELS)


def test_evaluate_models_keys():
    models = train_models(make_frame("train"))
    result = evaluate_models(models, make_frame("validation"))
    assert set(result) == set(ORDER)