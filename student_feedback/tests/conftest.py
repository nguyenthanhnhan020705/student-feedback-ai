"""Shared fixtures. Integration/parity tests need the local frozen bundle and fail loudly if absent."""
import socket
import subprocess
import sys
import time
import json
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='session')
def project_root():
    return ROOT


@pytest.fixture(scope='session')
def real_client():
    """TestClient over the real frozen bundle; a missing bundle is a failure, never a skip."""
    from fastapi.testclient import TestClient
    from feedback_ai.api.app import create_app
    from feedback_ai.config import Settings
    if not (ROOT / 'artifacts/serving/manifest.json').is_file():
        pytest.fail('Frozen bundle missing: run `feedback-ai --project-root . bundle import --source <old checkout>`')
    with TestClient(create_app(Settings.from_root(ROOT))) as client:
        assert client.get('/api/health').json()['ready'] is True
        yield client


@pytest.fixture(scope='session')
def server_url():
    """Real uvicorn process (own port) serving the packaged app, for browser tests."""
    if not (ROOT / 'artifacts/serving/manifest.json').is_file():
        pytest.fail('Frozen bundle missing for browser tests')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
    process = subprocess.Popen([sys.executable, '-B', '-m', 'feedback_ai', '--project-root', str(ROOT), 'serve', '--port', str(port)],
                               cwd=ROOT.parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f'http://127.0.0.1:{port}'
    try:
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            if process.poll() is not None:
                pytest.fail('server exited during startup')
            try:
                with urllib.request.urlopen(url + '/api/health', timeout=1) as response:
                    assert json.load(response)['ready'] is True
                break
            except OSError:
                time.sleep(.2)
        else:
            pytest.fail('server startup deadline')
        yield url
    finally:
        process.terminate(); process.wait(timeout=10)
