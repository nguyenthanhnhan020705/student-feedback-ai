"""Real-data workflow: data -> train -> evaluate, notebooks, and the wheel (needs data/raw + bundle)."""
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import nbformat
import pytest

from feedback_ai.common.hashing import digest
from feedback_ai.cli import main

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope='module')
def real_data():
    if not (ROOT / 'data/raw/train/sents.txt').is_file():
        pytest.fail('data/raw missing: run `feedback-ai --project-root . data acquire` or `data import`')


def serving_hashes():
    return {p.name: digest(p) for p in sorted((ROOT / 'artifacts/serving').rglob('*')) if p.is_file()}


def test_train_evaluate_without_touching_serving(real_data, tmp_path, capsys):
    before = serving_hashes()
    run = tmp_path / 'topic'
    assert main(['--project-root', str(ROOT), 'train', '--task', 'topic', '--output', str(run)]) == 0
    assert {'topic_pipeline.joblib', 'topic_metadata.json', 'comparison.json', 'confusion_matrix.png'} <= {p.name for p in run.iterdir()}
    result = json.loads((run / 'comparison.json').read_text(encoding='utf-8'))
    assert result['selection']['algorithm'] in {'nb', 'logistic_regression', 'linear_svm'}
    assert set(result['test']) == {'nb', 'logistic_regression', 'linear_svm'}
    out = tmp_path / 'eval'
    assert main(['--project-root', str(ROOT), 'evaluate', '--task', 'topic', '--artifact', str(run / 'topic_pipeline.joblib'), '--output', str(out)]) == 0
    metrics = json.loads((out / 'metrics.json').read_text(encoding='utf-8'))
    assert metrics['accuracy'] == pytest.approx(result['test'][result['selection']['algorithm']]['accuracy'])
    with pytest.raises(FileExistsError):
        main(['--project-root', str(ROOT), 'train', '--task', 'topic', '--output', str(run)])
    with pytest.raises(ValueError, match='serving'):
        main(['--project-root', str(ROOT), 'train', '--task', 'topic', '--output', str(ROOT / 'artifacts/serving/new')])
    assert serving_hashes() == before


def test_evaluate_rejects_modified_artifact(real_data, tmp_path):
    run = tmp_path / 'topic'
    main(['--project-root', str(ROOT), 'train', '--task', 'topic', '--output', str(run)])
    artifact = run / 'topic_pipeline.joblib'
    artifact.write_bytes(artifact.read_bytes() + b'\0')
    with pytest.raises(ValueError, match='checksum'):
        main(['--project-root', str(ROOT), 'evaluate', '--task', 'topic', '--artifact', str(artifact), '--output', str(tmp_path / 'eval')])


@pytest.mark.parametrize('name', ['01_eda', '02_sentiment', '03_topic'])
def test_notebook_code_cells_run_from_project(real_data, name, tmp_path):
    """Execute every code cell in a fresh interpreter with cwd inside the project (no kernel needed)."""
    notebook = nbformat.read(ROOT / 'notebooks' / f'{name}.ipynb', 4)
    code = 'import matplotlib\nmatplotlib.use("Agg")\n' + '\n'.join(c.source for c in notebook.cells if c.cell_type == 'code')
    env = {k: v for k, v in os.environ.items() if k.upper() != 'PYTHONPATH'}
    done = subprocess.run([sys.executable, '-c', code], cwd=ROOT / 'notebooks', env=env, capture_output=True, text=True, encoding='utf-8')
    assert done.returncode == 0, done.stderr[-1500:]


def test_wheel_contains_resources_and_runs_elsewhere(tmp_path):
    wheel_dir = tmp_path / 'wheel'
    build = subprocess.run([sys.executable, '-m', 'pip', 'wheel', str(ROOT), '--no-deps', '--no-build-isolation', '-w', str(wheel_dir)],
                           capture_output=True, text=True, cwd=tmp_path)
    assert build.returncode == 0, build.stderr[-1500:]
    wheel = next(wheel_dir.glob('*.whl'))
    names = zipfile.ZipFile(wheel).namelist()
    for needed in ('feedback_ai/resources/rules.json', 'feedback_ai/web/index.html', 'feedback_ai/web/mau-phan-hoi.xlsx',
                   'feedback_ai/web/app.js', 'feedback_ai/web/batch.js', 'feedback_ai/web/styles.css', 'feedback_ai/web/batch.css',
                   'feedback_ai/web/api.js', 'ml/preprocessing.py', 'reports/ct4_augmentation.py'):
        assert needed in names, needed
    assert not [n for n in names if n.startswith(('tests/', 'data/', 'artifacts/'))]
