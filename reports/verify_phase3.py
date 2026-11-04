"""Exercise real HTTP from an external cwd without training or changing artifacts."""
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "reports/evidence/phase-3"


def request(url, path, payload=None):
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url + path, data=payload, headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        data = response.read()
        return response.status, (json.loads(data) if "application/json" in response.headers.get("Content-Type", "") else bool(data))


def main():
    import joblib

    OUT.mkdir(parents=True, exist_ok=True)
    phase2 = json.loads((ROOT / "reports/evidence/phase-2/verification.json").read_text(encoding="utf-8"))
    protected = phase2["protected_hashes"]
    for path, digest in protected.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    models = {task: joblib.load(ROOT / f"models/{task}_pipeline.joblib") for task in ("sentiment", "topic")}
    result = {"python": platform.python_version(), "protected_files_unchanged": len(protected), "runs": []}
    with tempfile.TemporaryDirectory(prefix="sfai-phase3-") as external:
        for missing in (False, True):
            env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
            env.pop("SFAI_MODEL_DIR", None)
            if missing:
                env["SFAI_MODEL_DIR"] = external
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            url = f"http://127.0.0.1:{port}"
            with (OUT / f"http-server-{'missing' if missing else 'ready'}.txt").open("w", encoding="utf-8") as log:
                process = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "backend.main:app", "--app-dir", str(ROOT),
                     "--host", "127.0.0.1", "--port", str(port)],
                    cwd=external, env=env, stdout=log, stderr=log,
                )
                try:
                    deadline = time.monotonic() + 45
                    while time.monotonic() < deadline:
                        assert process.poll() is None, "server exited"
                        try:
                            status, health = request(url, "/api/health")
                            break
                        except OSError:
                            time.sleep(0.1)
                    else:
                        raise AssertionError("startup timed out")
                    assert status == 200 and health["ready"] is (not missing)
                    record = {"cwd_outside_repo": True, "health": health, "predictions": [], "errors": []}
                    for asset in ("/", "/app.js", "/api.js", "/styles.css"):
                        assert request(url, asset) == (200, True)
                    assert request(url, "/models/sentiment_pipeline.joblib")[0] == 404
                    assert request(url, "/api/predict")[0] == 405
                    for sentence in ("Giảng viên giải thích rõ ràng.", "Phòng học nóng và máy chiếu hỏng.",
                                     "  KHÔNG hài lòng với chương trình học!  ", "Hoạt động ngoại khóa thú vị."):
                        status, body = request(url, "/api/predict", json.dumps({"text": sentence}).encode())
                        if missing:
                            assert status == 503 and body["error"]["code"] == "MODEL_NOT_READY"
                        else:
                            expected = {task: str(model.predict([sentence])[0]) for task, model in models.items()}
                            assert status == 200 and body == {**expected, "contract_version": "1.0"}
                        record["predictions"].append({"input": sentence, "status": status, "response": body})
                    for payload in (b'\xff', b'{', b'{"text":""}', json.dumps({"text": "😀" * 5001}).encode()):
                        status, body = request(url, "/api/predict", payload)
                        assert status == 422 and body["error"]["code"] == "INVALID_INPUT"
                        assert body["contract_version"] == "1.0"
                        record["errors"].append({"status": status, "response": body})
                    result["runs"].append(record)
                finally:
                    process.terminate()
                    process.wait(timeout=15)
    for path, digest in protected.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    (OUT / "http-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"HTTP verification passed; {len(protected)} protected files unchanged; real/missing models, external cwd, static assets and errors checked.")


if __name__ == "__main__":
    main()
