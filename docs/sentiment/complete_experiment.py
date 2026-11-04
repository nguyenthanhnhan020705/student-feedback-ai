"""Run after training: record reload evidence and aggregate errors without publishing source text."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ml.data import load_dataset
from ml.predict_sentiment import predict_texts
import joblib


def main():
    out = ROOT / "reports/evidence/sentiment"
    out.mkdir(parents=True, exist_ok=True)
    artifact = ROOT / "models/sentiment_pipeline.joblib"
    pipeline = joblib.load(artifact)
    frame = load_dataset(ROOT / "data/raw")["test"]
    predicted = predict_texts(pipeline, frame["text"].tolist())
    confusion = {}
    examples = []
    for row, label in zip(frame.to_dict("records"), predicted):
        if row["sentiment"] != label:
            key = row["sentiment"] + " -> " + label
            confusion[key] = confusion.get(key, 0) + 1
            if sum(e["actual"] == row["sentiment"] for e in examples) < 5:
                examples.append({"id": row["id"], "actual": row["sentiment"], "predicted": label})
    # Fixed authored samples, not dataset excerpts; safe for Backend handoff.
    samples = ["Gi\u1ea3ng vi\u00ean gi\u1ea3ng d\u1ec5 hi\u1ec3u", "Ph\u00f2ng h\u1ecdc r\u1ea5t n\u00f3ng", "M\u00f4n h\u1ecdc c\u00f3 ba t\u00edn ch\u1ec9"]
    expected = predict_texts(pipeline, samples)
    code = "import joblib,json; from ml.predict_sentiment import predict_texts; print(json.dumps(predict_texts(joblib.load('models/sentiment_pipeline.joblib'), " + repr(samples) + "),ensure_ascii=False))"
    proc = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True, encoding="utf-8", env={**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8'})
    actual = json.loads(proc.stdout)
    assert actual == expected
    (out / "reload.json").write_text(json.dumps({"artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(), "samples": samples, "before": expected, "after_new_process": actual}, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "reports/metrics/sentiment/error_analysis.json").write_text(json.dumps({"n_rows": len(frame), "errors": sum(confusion.values()), "confusions": confusion, "examples_by_id": examples}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "requirements-local.txt").write_text(subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True), encoding="utf-8")
    print(json.dumps({"rows": len(frame), "errors": sum(confusion.values()), "reload_equal": actual == expected}))

if __name__ == "__main__":
    main()
