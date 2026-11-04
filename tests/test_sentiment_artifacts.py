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

def test_cli_fixture_lifecycle(tmp_path):
    import hashlib
    data_dir = tmp_path / "raw"
    for split, folder in [("train", "train"), ("validation", "dev"), ("test", "test")]:
        frame = make_frame(split)
        target = data_dir / folder
        target.mkdir(parents=True)
        (target / "sents.txt").write_text("\n".join(frame["text"]) + "\n", encoding="utf-8")
        mapping = {"negative": "0", "neutral": "1", "positive": "2"}
        (target / "sentiments.txt").write_text("\n".join(mapping[x] for x in frame["sentiment"]) + "\n", encoding="utf-8")
        (target / "topics.txt").write_text("3\n" * len(frame), encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"fixture": true}', encoding="utf-8")
    out, report, figures = (tmp_path / x for x in ("models", "metrics", "figures"))
    subprocess.run([sys.executable, "-m", "ml.train_sentiment", "--data-dir", str(data_dir),
                    "--manifest", str(manifest), "--output-dir", str(out),
                    "--report-dir", str(report), "--figure-dir", str(figures)],
                   cwd=ROOT, check=True, capture_output=True, text=True)
    comparison_path = report / "comparison.json"
    original = comparison_path.read_bytes()
    comparison = json.loads(original)
    metadata = json.loads((out / "sentiment_metadata.json").read_text(encoding="utf-8"))
    artifact = out / "sentiment_pipeline.joblib"
    assert metadata["artifact_sha256"] == hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert metadata["dataset_manifest_sha256"] == hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert set(comparison["validation"]) == {"nb", "logistic_regression", "linear_svm"}
    assert comparison["selection"]["algorithm"] == metadata["algorithm"]
    assert (figures / "confusion_matrix.png").stat().st_size > 0
    subprocess.run([sys.executable, "-m", "ml.evaluate_sentiment", "--data-dir", str(data_dir),
                    "--pipeline", str(artifact), "--output-dir", str(report)],
                   cwd=ROOT, check=True, capture_output=True, text=True)
    selected = json.loads((report / "selected_test.json").read_text(encoding="utf-8"))
    assert selected["test"] == comparison["test"][metadata["algorithm"]]
    assert comparison_path.read_bytes() == original
