"""Real CLI lifecycle with small authored corpus, isolated from project artifacts."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from ml.data import inspect_data
from ml.predict_topic import load_topic_pipeline, predict_texts

ROOT = Path(__file__).resolve().parents[1]


def run_module(module, *args):
    return subprocess.run([sys.executable, '-m', module, *map(str, args)], cwd=ROOT,
                          capture_output=True, text=True, encoding='utf-8',
                          env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'MPLBACKEND': 'Agg'})


@pytest.fixture
def corpus(tmp_path):
    raw = tmp_path / 'raw'
    for split in ('train', 'dev', 'test'):
        folder = raw / split
        folder.mkdir(parents=True)
        sentences = ['giảng viên dạy tốt', 'chương trình môn học',
                     'phòng học máy chiếu', 'hoạt động đoàn hội'] * 3
        (folder / 'sents.txt').write_text('\n'.join(sentences) + '\n', encoding='utf-8')
        (folder / 'sentiments.txt').write_text('2\n' * 12, encoding='utf-8')
        (folder / 'topics.txt').write_text('0\n1\n2\n3\n' * 3, encoding='utf-8')
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps(inspect_data(raw)), encoding='utf-8')
    return raw, manifest


def train_args(tmp_path, corpus):
    raw, manifest = corpus
    return ('--data-dir', raw, '--manifest', manifest, '--output-dir', tmp_path / 'models',
            '--report-dir', tmp_path / 'metrics', '--figure-dir', tmp_path / 'figures')


def test_cli_lifecycle_reload_and_evaluation_preserve_baseline(tmp_path, corpus):
    result = run_module('ml.train_topic', *train_args(tmp_path, corpus))
    assert result.returncode == 0, result.stderr
    artifact = tmp_path / 'models/topic_pipeline.joblib'
    metadata_path = artifact.with_name('topic_metadata.json')
    model, metadata = load_topic_pipeline(artifact, metadata_path)
    assert metadata['artifact_sha256'] == hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert metadata['dataset_manifest_sha256'] == hashlib.sha256(corpus[1].read_bytes()).hexdigest()
    assert (tmp_path / 'figures/confusion_matrix.png').is_file()
    texts = ['phòng học máy chiếu', 'hoạt động đoàn hội']
    assert predict_texts(model, texts) == ['facility', 'other']
    reload = run_module('ml.predict_topic', '--pipeline', artifact, '--metadata', metadata_path,
                        '--text', texts[0], '--text', texts[1])
    assert reload.returncode == 0, reload.stderr
    assert json.loads(reload.stdout) == ['facility', 'other']
    comparison_path = tmp_path / 'metrics/comparison.json'
    before = comparison_path.read_bytes()
    comparison = json.loads(before)
    assert set(comparison['test']) == {'nb', 'logistic_regression', 'linear_svm'}
    result = run_module('ml.evaluate_topic', '--data-dir', corpus[0], '--pipeline', artifact,
                        '--manifest', corpus[1], '--output-dir', tmp_path / 'metrics')
    assert result.returncode == 0, result.stderr
    selected = json.loads((tmp_path / 'metrics/selected_test.json').read_text())
    assert selected['test'] == comparison['test'][metadata['algorithm']]
    assert comparison_path.read_bytes() == before
    # Environment mismatch must be rejected even when artifact bytes are valid.
    original_metadata = metadata_path.read_bytes()
    for field, value in [('parameters', {}), ('trained_at', 'not-a-date'),
                         ('selection', {'algorithm': metadata['algorithm'], 'metric': 'macro_f1'})]:
        changed = json.loads(original_metadata)
        changed[field] = value
        metadata_path.write_text(json.dumps(changed), encoding='utf-8')
        with pytest.raises(ValueError):
            load_topic_pipeline(artifact, metadata_path)
    metadata_path.write_bytes(original_metadata)
    changed = json.loads(original_metadata)
    changed['package_versions']['scikit-learn'] = '0.0.0'
    metadata_path.write_text(json.dumps(changed), encoding='utf-8')
    with pytest.raises(ValueError, match='Package versions'):
        load_topic_pipeline(artifact, metadata_path)
    metadata_path.write_bytes(original_metadata)
    # A changed test file must not be silently evaluated under the old provenance.
    test_text = corpus[0] / 'test/sents.txt'
    original_text = test_text.read_bytes()
    test_text.write_bytes(original_text.replace(b' ', b'  ', 1))
    mismatched = run_module('ml.evaluate_topic', '--data-dir', corpus[0], '--pipeline', artifact,
                            '--manifest', corpus[1], '--output-dir', tmp_path / 'mismatched')
    assert mismatched.returncode != 0
    assert 'manifest mismatch' in mismatched.stderr.lower()
    assert not (tmp_path / 'mismatched/selected_test.json').exists()
    test_text.write_bytes(original_text)
    # Existing baseline evidence must remain intact on accidental retraining.
    retry = run_module('ml.train_topic', *train_args(tmp_path, corpus))
    assert retry.returncode != 0
    assert comparison_path.read_bytes() == before
    # Reject a corrupt artifact before deserialization.
    artifact.write_bytes(artifact.read_bytes() + b'corrupted')
    with pytest.raises(ValueError, match='checksum'):
        load_topic_pipeline(artifact, metadata_path)


def test_training_rejects_manifest_from_different_corpus(tmp_path, corpus):
    raw, _ = corpus
    with (raw / 'train/sents.txt').open('a', encoding='utf-8') as f:
        f.write('new sentence\n')
    for name in ('sentiments.txt', 'topics.txt'):
        with (raw / 'train' / name).open('a', encoding='utf-8') as f:
            f.write('0\n')
    result = run_module('ml.train_topic', *train_args(tmp_path, corpus))
    assert result.returncode != 0
    assert 'manifest' in result.stderr.lower() and 'mismatch' in result.stderr.lower()
    assert not (tmp_path / 'models/topic_pipeline.joblib').exists()
