"""Prove the project runs on its own: copy it elsewhere, install into a brand-new venv, run everything.

    python tools/verify_standalone.py --output <new empty dir> [--legacy-root <old checkout>] [--browser]

Steps (each recorded in <output>/report.json; the first failure stops the run and exits non-zero):
  1. copy project (no .venv/outputs/caches) next to data/ and artifacts/ (git-ignored payloads are copied on purpose)
  2. new venv + `pip install -r requirements/lock.txt` + wheel built from the copy (not an editable install)
  3. PYTHONPATH removed, cwd outside the project: module origins, serve+health+predict, data validate, train, evaluate
  4. pytest of the copy (unit, integration, parity [, browser]) against the installed wheel
  5. bundle bytes unchanged; legacy sources unchanged when --legacy-root and outputs/migration/source-hashes.json exist
"""
import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SKIP = shutil.ignore_patterns('.venv', 'outputs', '__pycache__', '.pytest_cache', '*.egg-info', 'build', 'dist')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_hashes(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(Path(root).rglob('*')) if p.is_file()}


def run(command, **kwargs):
    done = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', **kwargs)
    return done


def verify_standalone(output, legacy_root=None, browser=False):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    report = {'steps': [], 'ok': False}

    def step(name, ok, detail=''):
        report['steps'].append({'step': name, 'ok': bool(ok), 'detail': str(detail)[-1500:]})
        (output / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        if not ok:
            raise SystemExit(f'FAILED at {name}: {str(detail)[-800:]}')

    for part in ('data', 'artifacts'):
        if not (PROJECT / part).is_dir():
            step('payload', False, f'{part}/ missing: import data/bundle first')
    bundle_before = tree_hashes(PROJECT / 'artifacts/serving')
    copy = output / 'project'
    shutil.copytree(PROJECT, copy, ignore=SKIP)
    shutil.copytree(PROJECT / 'data', copy / 'data', dirs_exist_ok=True)
    shutil.copytree(PROJECT / 'artifacts', copy / 'artifacts', dirs_exist_ok=True)
    step('copy', (copy / 'pyproject.toml').is_file(), copy)

    venv = output / 'venv'
    step('venv', run([sys.executable, '-m', 'venv', str(venv)]).returncode == 0)
    py = str(venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python'))
    pip = [py, '-m', 'pip', 'install', '-q', '--disable-pip-version-check']
    done = run(pip + ['-r', str(copy / 'requirements/lock.txt')])
    step('install lock', done.returncode == 0, done.stderr)
    done = run(pip + ['setuptools', 'wheel', '-r', str(copy / 'requirements/test.txt')] + (['-r', str(copy / 'requirements/browser.txt')] if browser else []))
    step('install test tools', done.returncode == 0, done.stderr)
    wheels = output / 'wheels'
    done = run([py, '-m', 'pip', 'wheel', str(copy), '--no-deps', '-w', str(wheels), '-q', '--disable-pip-version-check'])
    step('build wheel', done.returncode == 0 and any(wheels.glob('*.whl')), done.stderr)
    done = run(pip + ['--no-deps', str(next(wheels.glob('*.whl')))])
    step('install wheel', done.returncode == 0, done.stderr)
    done = run([py, '-m', 'pip', 'check'])
    step('pip check', done.returncode == 0, done.stdout + done.stderr)

    env = {k: v for k, v in os.environ.items() if k.upper() != 'PYTHONPATH'}
    work = output / 'cwd'
    work.mkdir()
    done = run([py, '-c', 'import json,feedback_ai,ml,reports;print(json.dumps([m.__file__ for m in (feedback_ai,ml,reports)]))'], cwd=work, env=env)
    origins = json.loads(done.stdout.strip().splitlines()[-1]) if done.returncode == 0 else []
    inside = all(Path(o).resolve().is_relative_to(venv.resolve()) for o in origins)
    step('module origins', inside and len(origins) == 3, origins or done.stderr)

    cli = [py, '-m', 'feedback_ai', '--project-root', str(copy)]
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
    server = subprocess.Popen(cli + ['serve', '--port', str(port)], cwd=work, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        url = f'http://127.0.0.1:{port}'
        health = None
        for _ in range(200):
            try:
                with urllib.request.urlopen(url + '/api/health', timeout=1) as response:
                    health = json.load(response); break
            except OSError:
                time.sleep(.2)
        step('serve health', bool(health and health['ready'] is True), health)
        request = urllib.request.Request(url + '/api/v3/predict', data=json.dumps({'text': 'Thầy giảng bài rõ ràng và phòng học thì nóng.'}).encode(),
                                         headers={'content-type': 'application/json'})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.load(response)
        step('predict', body.get('sentiment') == 'mixed' and body.get('topics') == ['lecturer', 'facility'], body)
    finally:
        server.terminate(); server.wait(timeout=10)

    done = run(cli + ['data', 'validate'], cwd=work, env=env)
    step('data validate', done.returncode == 0, done.stderr)
    run_dir = output / 'run'
    done = run(cli + ['train', '--task', 'topic', '--output', str(run_dir / 'topic')], cwd=work, env=env)
    step('train topic', done.returncode == 0, done.stderr)
    done = run(cli + ['evaluate', '--task', 'topic', '--artifact', str(run_dir / 'topic/topic_pipeline.joblib'), '--output', str(run_dir / 'eval')], cwd=work, env=env)
    metrics = json.loads((run_dir / 'eval/metrics.json').read_text(encoding='utf-8')) if done.returncode == 0 else {}
    step('evaluate topic', 'accuracy' in metrics, metrics.get('accuracy', done.stderr))

    suites = ['tests/unit', 'tests/integration', 'tests/parity'] + (['tests/browser'] if browser else [])
    env_tests = dict(env, TV2_RUN_REAL_DATA='1')
    done = run([py, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', f'--basetemp={output / "pytest-tmp"}', *suites], cwd=copy, env=env_tests)
    tail = done.stdout.strip().splitlines()[-1] if done.stdout.strip() else done.stderr
    step('pytest ' + ' '.join(suites), done.returncode == 0 and ' failed' not in tail and ' error' not in tail, tail)

    step('bundle unchanged', tree_hashes(PROJECT / 'artifacts/serving') == bundle_before == tree_hashes(copy / 'artifacts/serving'))
    baseline = PROJECT / 'outputs/migration/source-hashes.json'
    if legacy_root and baseline.is_file():
        recorded = json.loads(baseline.read_text(encoding='utf-8'))
        changed = [k for k, v in recorded.items() if not (Path(legacy_root) / k).is_file() or sha(Path(legacy_root) / k) != v]
        step('legacy sources unchanged', not changed, changed[:10])
    report['ok'] = True
    (output / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy-root', type=Path)
    parser.add_argument('--browser', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify_standalone(args.output, args.legacy_root, args.browser), indent=2, ensure_ascii=False))
