"""Local operational rehearsal; never trains or modifies production artifacts.

Checks real UI/API/model behavior with external application networking denied.
The guard is process-local, not an OS-wide firewall or browser background audit.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def loopback(host):
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host == "localhost"


def serve(args):
    # Install before importing the app or its dependencies. Reject DNS as well
    # as direct-IP connects/sendto, including native socket calls audited by Python.
    def guard(event, values):
        host = None
        if event == "socket.getaddrinfo":
            host = values[0]
        elif event in ("socket.connect", "socket.sendto"):
            address = values[-1]
            if isinstance(address, tuple):
                host = address[0]
        if host is not None and not loopback(host):
            with args.network_log.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"event": event, "host": str(host)}) + "\n")
            raise PermissionError("Phase 5: external application network denied")

    sys.addaudithook(guard)
    try:
        socket.create_connection(("192.0.2.1", 443), timeout=1)
    except PermissionError:
        pass
    else:
        raise AssertionError("Network guard negative control failed")
    sys.path.insert(0, str(args.project))
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=args.port)


def health(url):
    with urllib.request.urlopen(url + "/api/health", timeout=2) as response:
        return json.load(response)


@contextmanager
def server(project, output, external, port, name, missing=False):
    network_log = output / f"{name}-network.jsonl"
    network_log.write_text("", encoding="utf-8")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    env.pop("SFAI_MODEL_DIR", None)
    if missing:
        env["SFAI_MODEL_DIR"] = str(Path(external) / "absent-models")
    started = time.perf_counter()
    with (output / f"{name}-server.txt").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--serve", "--project", str(project),
             "--port", str(port), "--network-log", str(network_log)],
            cwd=external, env=env, stdout=log, stderr=log,
        )
        try:
            deadline = time.monotonic() + 45
            url = f"http://127.0.0.1:{port}"
            while time.monotonic() < deadline:
                assert process.poll() is None, f"Server exited: {name}"
                try:
                    status = health(url)
                    break
                except OSError:
                    time.sleep(0.1)
            else:
                raise AssertionError(f"Startup timeout: {name}")
            assert status == {"status": "ok", "ready": not missing,
                              "models": {task: "missing" if missing else "ready"
                                         for task in ("sentiment", "topic")},
                              "contract_version": "1.0"}, status
            record = {"name": name, "startup_seconds": time.perf_counter() - started,
                      "health": status, "cwd_outside_project": True}
            yield url, record
        finally:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    # Exactly the deliberate guard probe, no application external request.
    denied = [json.loads(line) for line in network_log.read_text(encoding="utf-8").splitlines()]
    assert len(denied) == 1 and denied[0]["host"] == "192.0.2.1", denied
    record["network_guard_control_blocked"] = True
    record["application_external_attempts"] = 0
    record["process_stopped"] = process.poll() is not None


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main(args):
    from playwright.sync_api import expect, sync_playwright
    project, output = args.project.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    protected = json.loads((project / "reports/evidence/phase-2/verification.json").read_text(encoding="utf-8"))["protected_hashes"]
    def check_hashes():
        for relative, digest in protected.items():
            assert hashlib.sha256((project / relative).read_bytes()).hexdigest() == digest, relative
    check_hashes()
    result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "project": str(project),
              "python": sys.version, "protected_files_unchanged": len(protected), "browsers": [],
              "network_scope": "Python server socket audit + browser context HTTP routing; not OS-wide offline"}
    with tempfile.TemporaryDirectory(prefix="sfai-phase5-") as external, sync_playwright() as playwright:
        for channel in ("chrome", "msedge"):
            browser = playwright.chromium.launch(headless=True, channel=channel)
            try:
                context = browser.new_context(viewport={"width": 1280, "height": 900}, service_workers="block")
                attempts = []
                def route_request(route):
                    if loopback(urlsplit(route.request.url).hostname or ""):
                        route.continue_()
                    else:
                        attempts.append(route.request.url)
                        route.abort("internetdisconnected")
                context.route("**/*", route_request)
                page = context.new_page()
                page.set_default_timeout(15000)
                port = free_port()
                entry = {"browser": channel, "version": browser.version, "runs": [], "predictions": []}
                def predict(text):
                    page.locator("#text").fill(text)
                    start = time.perf_counter()
                    with page.expect_response("**/api/predict") as response:
                        page.locator("#go").click()
                    assert response.value.status == 200
                    body = response.value.json()
                    labels = {"negative": "Tiêu cực", "neutral": "Trung tính", "positive": "Tích cực",
                              "lecturer": "Giảng viên", "curriculum": "Chương trình đào tạo",
                              "facility": "Cơ sở vật chất", "other": "Khác"}
                    assert body["contract_version"] == "1.0"
                    expect(page.locator("#out .res b")).to_have_text([labels[body["sentiment"]], labels[body["topic"]]])
                    expect(page.locator("#mockBanner")).to_be_hidden()
                    entry["predictions"].append({"input": text, "response": body,
                                                  "click_to_result_seconds": time.perf_counter() - start})
                with server(project, output, external, port, channel + "-cold") as (url, run):
                    page.goto(url)
                    expect(page.locator("#health")).to_have_text("Mô hình sẵn sàng")
                    # Exercise the browser guard without issuing an external network request.
                    assert page.evaluate("async () => {try {await fetch('https://phase5.invalid/probe'); return false;} catch {return true;}}")
                    assert attempts == ["https://phase5.invalid/probe"]
                    attempts.clear()
                    page.locator("#text").fill("   ")
                    expect(page.locator("#go")).to_be_disabled()
                    page.locator("#text").fill("🙂" * 5001)
                    expect(page.locator("#go")).to_be_disabled()
                    bad = context.request.post(url + "/api/predict", data={"text": ""})
                    assert bad.status == 422 and bad.json()["error"]["code"] == "INVALID_INPUT"
                    predict("Giảng viên giải thích bài tập rõ ràng và tận tình.")
                    page.screenshot(path=str(output / f"{channel}-offline-real.png"), full_page=True)
                    entry["runs"].append(run)
                page.locator("#go").click()
                expect(page.locator("#out p")).to_contain_text("Không kết nối")
                expect(page.locator("#text")).to_have_value(entry["predictions"][-1]["input"])
                expect(page.locator("#out .res")).to_have_count(0)
                with server(project, output, external, port, channel + "-restart") as (url, run):
                    page.locator("#recheck").click()
                    expect(page.locator("#health")).to_have_text("Mô hình sẵn sàng")
                    predict("Phòng học nóng và máy chiếu không hoạt động.")
                    entry["runs"].append(run)
                with server(project, output, external, port, channel + "-missing", missing=True) as (url, run):
                    page.locator("#recheck").click()
                    expect(page.locator("#health")).to_contain_text("Mô hình chưa sẵn sàng")
                    expect(page.locator("#go")).to_be_disabled()
                    expect(page.locator("#text")).to_have_value(entry["predictions"][-1]["input"])
                    response = context.request.post(url + "/api/predict", data={"text": "Một câu mới."})
                    assert response.status == 503 and response.json()["error"]["code"] == "MODEL_NOT_READY"
                    page.screenshot(path=str(output / f"{channel}-missing-models.png"), full_page=True)
                    entry["runs"].append(run)
                with server(project, output, external, port, channel + "-restored") as (url, run):
                    page.locator("#recheck").click()
                    expect(page.locator("#go")).to_be_enabled()
                    predict("Chương trình học có nhiều bài tập thực hành hữu ích.")
                    entry["runs"].append(run)
                assert attempts == [], attempts
                entry.update(browser_guard_control_blocked=True, application_external_attempts=attempts,
                             blank_and_overlimit_rejected=True, restart_and_recovery=True)
                result["browsers"].append(entry)
            finally:
                browser.close()
    check_hashes()
    dump(output / "rehearsal.json", result)
    print("PASS: Chrome/Edge real offline-guarded UI, cold start/restart/missing/restored, 59 protected hashes unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/evidence/phase-5")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int)
    parser.add_argument("--network-log", type=Path)
    arguments = parser.parse_args()
    serve(arguments) if arguments.serve else main(arguments)
