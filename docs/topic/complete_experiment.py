"""Analyze the frozen Topic model; no fitting or selection, no source-text export."""
from collections import Counter
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import joblib
from ml.data import load_split
from ml.evaluate_topic import evaluate_models, verify_dataset_manifest
from ml.predict_topic import load_topic_pipeline, predict_texts


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    evidence = ROOT / 'reports/evidence/topic'
    evidence.mkdir(parents=True, exist_ok=True)
    artifact = ROOT / 'models/topic_pipeline.joblib'
    pipeline, metadata = load_topic_pipeline(artifact, artifact.with_name('topic_metadata.json'))
    manifest_path = ROOT / 'reports/data/manifest.json'
    if verify_dataset_manifest(ROOT / 'data/raw', manifest_path) != metadata['dataset_manifest_sha256']:
        raise ValueError('Dataset manifest mismatch with trained artifact')
    frame = load_split(ROOT / 'data/raw', 'test')
    predictions = predict_texts(pipeline, frame.text.tolist())
    pairs = Counter()
    examples = []
    for row, predicted in zip(frame.to_dict('records'), predictions):
        if row['topic'] != predicted:
            pair = f"{row['topic']} -> {predicted}"
            pairs[pair] += 1
            if sum(item['actual'] == row['topic'] for item in examples) < 5:
                examples.append({'id': row['id'], 'actual': row['topic'], 'predicted': predicted})
    metrics_dir = ROOT / 'reports/metrics/topic'
    comparison = json.loads((metrics_dir / 'comparison.json').read_text(encoding='utf-8'))
    scores = evaluate_models({metadata['algorithm']: pipeline}, frame)[metadata['algorithm']]
    if scores != comparison['test'][metadata['algorithm']]:
        raise ValueError('Reloaded model metrics differ from frozen comparison')
    selected = {'contract_version': '1.0', 'task': 'topic', 'algorithm': metadata['algorithm'],
                'dataset_manifest_sha256': metadata['dataset_manifest_sha256'], 'test': scores}
    selected_path = metrics_dir / 'selected_test.json'
    if selected_path.exists():
        if json.loads(selected_path.read_text(encoding='utf-8')) != selected:
            raise ValueError('Existing selected_test evidence differs')
    else:
        write_json(selected_path, selected)
    write_json(metrics_dir / 'error_analysis.json', {
        'artifact_sha256': metadata['artifact_sha256'], 'n_rows': len(frame),
        'errors': sum(pairs.values()), 'confusions': dict(pairs.most_common()),
        'examples_by_id': examples})

    # Authored examples are independent of the corpus and are not accuracy evidence.
    samples = ['Giảng viên giảng bài dễ hiểu', 'Chương trình có nhiều môn học',
               'Phòng học thiếu máy chiếu', 'Hoạt động đoàn hội rất vui',
               'Giảng viên dạy tốt nhưng phòng học quá nóng']
    before = predict_texts(pipeline, samples)
    # Round-trip the already fitted winner; no retraining or test-driven tuning.
    with tempfile.TemporaryDirectory() as temp:
        roundtrip = Path(temp) / 'roundtrip.joblib'
        joblib.dump(pipeline, roundtrip)
        code = ('import json,joblib,sys; from ml.predict_topic import predict_texts; '
                'print(json.dumps(predict_texts(joblib.load(sys.argv[1]), '
                'json.loads(sys.argv[2])), ensure_ascii=False))')
        result = subprocess.run([sys.executable, '-c', code, str(roundtrip),
                                 json.dumps(samples, ensure_ascii=False)], cwd=ROOT,
                                capture_output=True, text=True, encoding='utf-8', check=True,
                                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    after = json.loads(result.stdout)
    if before != after:
        raise ValueError('Round-trip predictions changed')
    write_json(evidence / 'reload.json', {
        'artifact_sha256': metadata['artifact_sha256'],
        'method': 'Reserialize fitted winner, compare before serialization and fresh-process reload; no fit',
        'samples': samples, 'before': before, 'after_new_process': after})
    write_json(evidence / 'environment.json', {
        'python': platform.python_version(), 'platform': platform.platform(),
        'packages': metadata['package_versions'],
        'manifest_status': json.loads(manifest_path.read_text(encoding='utf-8'))['source']['approval_status'],
        'scope': 'Local TV4 completion requested 2026-10-29; not leader lock or license approval'})
    (evidence / 'requirements-local.txt').write_text(subprocess.check_output(
        [sys.executable, '-m', 'pip', 'freeze'], text=True), encoding='utf-8')
    checked = subprocess.run([sys.executable, '-m', 'pip', 'check'], capture_output=True, text=True)
    (evidence / 'pip-check.txt').write_text(checked.stdout + checked.stderr, encoding='utf-8')
    checked.check_returncode()
    print(json.dumps({'algorithm': metadata['algorithm'], 'test': scores,
                      'errors': sum(pairs.values()), 'reload_equal': before == after}, ensure_ascii=False))


if __name__ == '__main__':
    main()
