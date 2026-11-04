"""Create an internal-only local demo ZIP and verify the extracted application.

No Git writes, no upload, no training, no venv copy. Refuses an existing destination.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request
import zipfile

from verify_phase5 import ROOT, dump, free_port, server


def main(destination):
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    # Explicit project areas only: no .git/.env/.venv/.local-tools or nested checkout.
    areas = ("backend", "frontend", "ml", "tests", "notebooks", "models", "data/raw",
             "data/processed", "requirements", "docs", "reports/data", "reports/metrics",
             "reports/figures", "reports/evidence")
    extensions = {".py", ".js", ".html", ".css", ".md", ".json", ".jsonl", ".txt",
                  ".csv", ".ipynb", ".png", ".joblib"}
    files = set()
    for area in areas:
        for path in (ROOT / area).rglob("*"):
            relative = path.relative_to(ROOT)
            # A ZIP cannot embed its own final hash. Never embed a previous
            # package receipt or an active packaging log as this ZIP's evidence.
            if (relative.parent.as_posix() == "reports/evidence/phase-5"
                    and path.name.startswith("package-")):
                continue
            if (path.is_file() and path.suffix in extensions
                    and not any(part.startswith(".") or part == "__pycache__" for part in relative.parts)):
                files.add(path)
    for pattern in ("requirements*.txt",):
        files.update(ROOT.glob(pattern))
    files.update(ROOT / name for name in ("README.md", "DEMO.md", "CONTRIBUTING.md", "pytest.ini", ".env.example"))
    files.update((ROOT / "reports").glob("*.py"))
    files.update((ROOT / "reports").glob("*.md"))
    inventory = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in sorted(files)}
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "internal_local_only": True,
                "source_license": "unknown", "files_sha256": inventory,
                "excluded": ["Git", "venvs", "Python/browser binaries", "secrets", "wheel cache"]}
    dump(destination / "package-manifest.json", manifest)
    archive = destination / "student-feedback-ai-local.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
        for relative in inventory:
            bundle.write(ROOT / relative, relative)
        bundle.write(destination / "package-manifest.json", "package-manifest.json")
    # Fresh extraction outside the project: imports/static/model paths must work
    # without source-tree files or data paths leaking in from the original checkout.
    with tempfile.TemporaryDirectory(prefix="sfai-package-") as temporary:
        extracted = Path(temporary) / "demo"
        with zipfile.ZipFile(archive) as bundle:
            assert bundle.testzip() is None
            bundle.extractall(extracted)
        for relative, expected in inventory.items():
            assert hashlib.sha256((extracted / relative).read_bytes()).hexdigest() == expected, relative
        with server(extracted, destination, temporary, free_port(), "extracted-package") as (url, run):
            assets = {}
            for route in ("/", "/app.js", "/api.js", "/styles.css"):
                with urllib.request.urlopen(url + route, timeout=10) as response:
                    payload = response.read()
                    assert response.status == 200 and payload
                    assets[route] = len(payload)
            request = urllib.request.Request(url + "/api/predict",
                data=json.dumps({"text": "Giảng viên giải thích bài tập rõ ràng và tận tình."}).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(request, timeout=10) as response:
                prediction = json.load(response)
                assert response.status == 200 and prediction["contract_version"] == "1.0"
                # Expected from independent, saved real rehearsal, not from this HTTP call.
                rehearsal = json.loads((ROOT / "reports/evidence/phase-5/rehearsal.json").read_text(encoding="utf-8"))
                assert prediction == rehearsal["browsers"][0]["predictions"][0]["response"]
        result = {"archive": str(archive), "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                  "archive_bytes": archive.stat().st_size, "verified_files": len(inventory),
                  "extracted_application": run, "assets_bytes": assets, "prediction": prediction,
                  "environment": "Existing locked Python venv; not a new install on a different computer"}
    dump(destination / "package-verification.json", result)
    dump(ROOT / "reports/evidence/phase-5/package-verification.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=ROOT / ".local-tools/phase5-delivery")
    main(parser.parse_args().destination)
