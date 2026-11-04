"""Reproducible local environment/startup evidence; no training or source edits."""
import hashlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/evidence/phase-1'
OUT.mkdir(parents=True, exist_ok=True)

def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True, encoding='utf-8').strip()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory():
    source = ROOT.parents[1]
    result = {'time_utc': datetime.now(timezone.utc).isoformat(), 'sources': {}, 'comparisons': {}}
    for name, path in [('TV2-TV4', source), ('TV5', source / '.local-tools/backend-tv5'), ('integration', ROOT)]:
        result['sources'][name] = {'path': str(path), 'branch': git(path, 'branch', '--show-current'), 'commit': git(path, 'rev-parse', 'HEAD'), 'status': git(path, 'status', '--porcelain')}
    result['sources']['TV6'] = {'branch': 'feature/frontend-dashboard', 'commit': git(source, 'rev-parse', 'feature/frontend-dashboard')}
    for name, base, folders in [('TV2-TV4', source, ['ml', 'notebooks', 'models', 'data/raw', 'data/processed']), ('TV5', source / '.local-tools/backend-tv5', ['backend'])]:
        files = {}
        for folder in folders:
            for p in (base / folder).rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts:
                    rel = p.relative_to(base).as_posix()
                    target = ROOT / rel
                    files[rel] = {'source_sha256': digest(p), 'integration_sha256': digest(target) if target.exists() else None}
        result['comparisons'][name] = files
    result['comparisons']['TV6'] = {}
    for p in (ROOT / 'frontend').glob('*'):
        if p.is_file():
            rel = p.relative_to(ROOT).as_posix()
            data = subprocess.check_output(['git', '-C', str(source), 'show', 'feature/frontend-dashboard:' + rel])
            result['comparisons']['TV6'][rel] = {'source_sha256': hashlib.sha256(data).hexdigest(), 'integration_sha256': digest(p), 'same_text_ignoring_final_newline': data.decode('utf-8').rstrip('\r\n') == p.read_text(encoding='utf-8').rstrip('\r\n')}
    target = ROOT / 'reports/evidence/phase-6/source-inventory.json'
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')

def verify():
    import fastapi, pandas, numpy, scipy, sklearn, joblib, matplotlib, nbformat
    versions = {name: md.version(name) for name in ['numpy', 'scipy', 'pandas', 'scikit-learn', 'joblib', 'fastapi', 'nbformat']}
    for task in ['sentiment', 'topic']:
        metadata = json.loads((ROOT / f'models/{task}_metadata.json').read_text())
        assert all(versions[k] == v for k, v in metadata['package_versions'].items())
        assert digest(ROOT / 'models' / metadata['artifact_filename']) == metadata['artifact_sha256']
    result = {'python': sys.version, 'packages': versions, 'startup': []}
    with tempfile.TemporaryDirectory() as temp:
        for missing in [False, True]:
            env = os.environ.copy()
            env.pop('SFAI_MODEL_DIR', None)
            if missing:
                env['SFAI_MODEL_DIR'] = temp
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            with (OUT / f'server-{missing}.txt').open('w', encoding='utf-8') as log:
                proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.main:app', '--app-dir', str(ROOT), '--host', '127.0.0.1', '--port', str(port)], cwd=temp, env=env, stdout=log, stderr=log)
                try:
                    for _ in range(120):
                        try:
                            with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=1) as response:
                                health = json.load(response)
                            break
                        except OSError:
                            assert proc.poll() is None, 'server exited'
                            time.sleep(.5)
                    else:
                        raise AssertionError('startup timeout')
                    assert health['ready'] is (not missing), health
                    for asset in ['/', '/app.js', '/api.js', '/styles.css']:
                        with urllib.request.urlopen(f'http://127.0.0.1:{port}{asset}') as response:
                            assert response.status == 200 and response.read()
                    result['startup'].append({'missing_models': missing, 'cwd_outside_repo': True, 'health': health, 'static_assets': 'passed'})
                finally:
                    proc.terminate()
                    proc.wait(timeout=15)
    (OUT / 'environment-startup.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    inventory()
    verify()
