"""Frozen bundle: integrity, tamper detection and import isolation (real artifacts)."""
import json
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from feedback_ai.common.hashing import digest
from feedback_ai.inference.bundle import verify_manifest

pytestmark = pytest.mark.integration
SERVING = Path(__file__).resolve().parents[2] / 'artifacts/serving'


@pytest.fixture
def bundle_copy(tmp_path):
    if not (SERVING / 'manifest.json').is_file():
        pytest.fail('Frozen bundle missing')
    target = tmp_path / 'serving'
    shutil.copytree(SERVING, target)
    return target


def test_real_bundle_verifies():
    manifest = verify_manifest(SERVING / 'manifest.json')
    assert len(manifest['files']) == 8
    for name, checksum in manifest['files'].items():
        assert digest(SERVING / name) == checksum


def test_tampered_artifact_is_rejected(bundle_copy):
    artifact = bundle_copy / 'ct4/research-selected/topic_pipeline.joblib'
    artifact.write_bytes(artifact.read_bytes() + b'\0')
    with pytest.raises(ValueError, match='modified'):
        verify_manifest(bundle_copy / 'manifest.json')


def test_missing_file_is_rejected(bundle_copy):
    (bundle_copy / 'ct5/thresholds.json').unlink()
    with pytest.raises(ValueError):
        verify_manifest(bundle_copy / 'manifest.json')


def test_broken_bundle_reports_not_ready_but_serves_ui(bundle_copy, tmp_path):
    from fastapi.testclient import TestClient
    from feedback_ai.api.app import create_app
    from feedback_ai.config import Settings
    (bundle_copy / 'ct5/thresholds.json').write_text('{}', encoding='utf-8')
    root = tmp_path / 'project'
    (root / 'artifacts').mkdir(parents=True)
    shutil.move(str(bundle_copy), root / 'artifacts/serving')
    with TestClient(create_app(Settings.from_root(root))) as client:
        assert client.get('/').status_code == 200
        assert client.get('/api/health').json()['ready'] is False
        assert client.post('/api/v3/predict', json={'text': 'Tốt'}).status_code == 503


ISOLATION_SCRIPT = textwrap.dedent('''
    import builtins, io, json, os, sys
    root = sys.argv[1]
    parent = os.path.dirname(root)
    legacy = parent.lower() if os.path.isdir(os.path.join(parent, 'demo_v3')) else None  # an old checkout beside us, if any
    def audit(event, args):
        if legacy and event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            path = os.fsdecode(args[0]).lower().replace('/', '\\\\')
            if path.startswith(legacy + '\\\\') and not path.startswith(root.lower() + '\\\\') and '\\\\.git' not in path:
                raise RuntimeError('legacy path touched: ' + path)
    sys.addaudithook(audit)
    from fastapi.testclient import TestClient
    from feedback_ai.api.app import create_app
    from feedback_ai.config import Settings
    with TestClient(create_app(Settings.from_root(root))) as client:
        assert client.get('/api/health').json()['ready'] is True
        assert client.post('/api/v3/predict', json={'text': 'Thầy giảng bài rõ ràng.'}).status_code == 200
    import ml.preprocessing, reports.ct4_augmentation, feedback_ai
    origins = {m.__name__: m.__file__ for m in (ml.preprocessing, reports.ct4_augmentation, feedback_ai)}
    print(json.dumps(origins))
''')


def test_runs_without_legacy_sources(tmp_path):
    """Pickle callbacks resolve to this project's shims and no legacy path is opened (cwd elsewhere)."""
    root = str(Path(__file__).resolve().parents[2])
    env = {k: v for k, v in __import__('os').environ.items() if k.upper() != 'PYTHONPATH'}
    done = subprocess.run([sys.executable, '-c', ISOLATION_SCRIPT, root], cwd=tmp_path, env=env,
                          capture_output=True, text=True, encoding='utf-8')
    assert done.returncode == 0, done.stderr[-2000:]
    origins = json.loads(done.stdout.strip().splitlines()[-1])
    allowed = (Path(root).resolve(), Path(sys.prefix).resolve())  # source tree (editable) or this env's site-packages (wheel)
    for name, origin in origins.items():
        assert any(Path(origin).resolve().is_relative_to(a) for a in allowed), (name, origin)
        assert 'demo_v' not in Path(origin).parts


def test_negative_control_detects_legacy_access(tmp_path):
    """Simulate an old checkout (a `demo_v3` folder beside the project) and prove the hook blocks reading it."""
    legacy = tmp_path / 'old-checkout'
    (legacy / 'demo_v3').mkdir(parents=True)
    (legacy / 'demo_v3/rules.json').write_text('{}', encoding='utf-8')
    fake_root = legacy / 'student_feedback'
    fake_root.mkdir()
    script = ISOLATION_SCRIPT.split('from fastapi')[0] + f'open({str(legacy / "demo_v3/rules.json")!r}).close()' + chr(10)
    done = subprocess.run([sys.executable, '-c', script, str(fake_root)], cwd=tmp_path, capture_output=True, text=True)
    assert done.returncode != 0 and 'legacy path touched' in done.stderr
