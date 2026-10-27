"""Kiểm tra lưu/tải artifact và predict_texts (fixture, tiến trình mới)."""
import json
import subprocess
import sys
from pathlib import Path

import joblib
import pytest

from ml.predict_sentiment import predict_texts
from ml.train_sentiment import train_models
from tests.test_sentiment_training import make_frame

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ["giảng viên dạy rất hay", "phòng học quá nóng và bẩn", "lớp học diễn ra vào buổi sáng"]


def test_predict_texts_behaviour():
    pipe = train_models(make_frame("train"))["logistic_regression"]
    assert predict_texts(pipe, []) == []
    out = predict_texts(pipe, SAMPLES)
    assert len(out) == len(SAMPLES)
    assert set(out) <= {"negative", "neutral", "positive"}
    assert predict_texts(pipe, SAMPLES[::-1]) == out[::-1]  # giữ thứ tự


@pytest.mark.parametrize("bad", [[""], ["   "], [123], ["ok", None]])
def test_predict_texts_rejects_bad_items(bad):
    pipe = train_models(make_frame("train"))["nb"]
    with pytest.raises(ValueError):
        predict_texts(pipe, bad)


def test_reload_in_new_process_same_predictions(tmp_path):
    pipe = train_models(make_frame("train"))["linear_svm"]
    path = tmp_path / "sentiment_pipeline.joblib"
    joblib.dump(pipe, path)
    before = predict_texts(pipe, SAMPLES)
    code = ("import json, joblib; from ml.predict_sentiment import predict_texts; "
            f"p = joblib.load(r'{path}'); "
            f"print(json.dumps(predict_texts(p, {SAMPLES!r}), ensure_ascii=False))")
    proc = subprocess.run([sys.executable, "-c", code], cwd=ROOT,
                          capture_output=True, text=True, check=True)
    assert json.loads(proc.stdout.strip().splitlines()[-1]) == before


def test_real_artifact_present_and_loadable():
    path = ROOT / "models" / "sentiment_pipeline.joblib"
    if not path.exists():
        pytest.skip("Chưa có artifact thật - KHÔNG tính là đạt nghiệm thu")
    assert predict_texts(joblib.load(path), SAMPLES)