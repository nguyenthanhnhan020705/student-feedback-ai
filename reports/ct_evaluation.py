"""CT1 offline evaluation. No fit, test selection, serving changes or overwrite."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone
from importlib.metadata import version

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from ml.labels import SENTIMENT_LABELS, TOPIC_LABELS

LABELS = {'sentiment': list(SENTIMENT_LABELS), 'topic': list(TOPIC_LABELS)}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_new_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def verify_inventory(root, inventory):
    for name, expected in inventory.items():
        path = Path(root) / name
        if not path.is_file() or digest(path) != expected:
            raise ValueError(f'Protected input missing or changed: {name}')


def score_labels(truth, predictions, labels):
    if (not truth or len(truth) != len(predictions)
            or any(x not in labels for x in truth)
            or any(x not in labels for x in predictions)):
        raise ValueError('Nonempty aligned canonical labels required')
    p, r, f, support = precision_recall_fscore_support(
        truth, predictions, labels=labels, zero_division=0)
    mp, mr, mf, _ = precision_recall_fscore_support(
        truth, predictions, labels=labels, average='macro', zero_division=0)
    return dict(accuracy=float(accuracy_score(truth, predictions)),
        macro_precision=float(mp), macro_recall=float(mr), macro_f1=float(mf),
        per_class=[dict(label=label, precision=float(p[i]), recall=float(r[i]),
                        f1=float(f[i]), support=int(support[i])) for i, label in enumerate(labels)],
        confusion_matrix=confusion_matrix(truth, predictions, labels=labels).tolist(),
        label_order=labels, n_rows=len(truth))


def score_cases(cases, predictions):
    if len(cases) != len(predictions) or len({c['id'] for c in cases}) != len(cases):
        raise ValueError('Case/prediction alignment or duplicate case ID')
    rows = []
    for case, pred in zip(cases, predictions):
        row = {**case, 'predicted': pred}
        for task in LABELS:
            expected = case[task]
            if (pred.get(task) not in LABELS[task]
                    or expected is not None and expected not in LABELS[task]):
                raise ValueError(f'Invalid {task} label in {case["id"]}')
            row[task + '_correct'] = None if expected is None else pred[task] == expected
        row['joint_correct'] = (None if any(row[t + '_correct'] is None for t in LABELS)
                                else all(row[t + '_correct'] for t in LABELS))
        rows.append(row)

    def counts(items):
        result = {}
        for task in [*LABELS, 'joint']:
            scored = [r[task + '_correct'] for r in items if r[task + '_correct'] is not None]
            result[task] = dict(scored=len(scored), correct=sum(scored),
                               accuracy=sum(scored) / len(scored) if scored else None)
        return result

    return {**counts(rows), 'rows': rows,
            'groups': {g: counts([r for r in rows if r['group'] == g])
                       for g in sorted({r['group'] for r in rows})},
            'status': 'exploratory_assistant_proposed_labels_not_human_reviewed'}


def evaluate(root, pipelines, cases, *, split='validation'):
    if split != 'validation':
        raise ValueError('Development evaluator permits validation only')
    from ml.data import load_split
    frame = load_split(Path(root) / 'data/raw', split)
    predictions = {task: list(pipelines[task].predict(frame.text.tolist())) for task in LABELS}
    metrics = {task: score_labels(frame[task].tolist(), predictions[task], LABELS[task])
               for task in LABELS}
    case_predictions = {task: list(pipelines[task].predict([c['text'] for c in cases]))
                        for task in LABELS}
    for task, values in case_predictions.items():
        if len(values) != len(cases) or any(value not in LABELS[task] for value in values):
            raise ValueError(f'Invalid {task} case prediction count or labels')
    cases_result = score_cases(cases, [{task: str(case_predictions[task][i]) for task in LABELS}
                                      for i in range(len(cases))])
    joint = sum(all(predictions[t][i] == frame[t].iloc[i] for t in LABELS)
                for i in range(len(frame)))
    return dict(split=split, metrics=metrics,
        joint=dict(correct=joint, n_rows=len(frame), accuracy=joint / len(frame)),
        prediction_rows=[dict(id=frame.id.iloc[i], **{t: str(predictions[t][i]) for t in LABELS})
                         for i in range(len(frame))], known_cases=cases_result)


def protected_files(root):
    paths = set()
    for pattern in ['ml/*.py', 'backend/*.py', 'backend/routes/*.py', 'frontend/*',
                    'models/*_pipeline.joblib', 'models/*_metadata.json',
                    'data/raw/**/*.txt', 'reports/metrics/*/*.json', 'requirements*lock.txt']:
        paths.update(p for p in root.glob(pattern) if p.is_file())
    for name in ['reports/data/manifest.json', 'reports/data/source.json',
                 'reports/quality/known-cases.json', 'docs/quality/ct1-protocol.md',
                 'reports/ct_evaluation.py']:
        paths.add(root / name)
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(paths)}


def create_baseline(root, output, snapshot):
    root, output, snapshot = Path(root), Path(output), Path(snapshot)
    if output.exists() or snapshot.exists():
        raise FileExistsError('Baseline output or snapshot already exists; choose a new location')
    from backend.model_service import ModelService
    service = ModelService(root / 'models')
    if not service.loaded:
        raise ValueError(f'Both trusted models must be ready: {service.status}')
    case_data = read(root / 'reports/quality/known-cases.json')
    cases = case_data['cases']
    inventory = protected_files(root)
    pipelines = {t: getattr(service, t + '_model') for t in LABELS}
    results = evaluate(root, pipelines, cases)
    historical_test = {}
    for task in LABELS:
        comparison = read(root / f'reports/metrics/{task}/comparison.json')
        winner = comparison['selection']['algorithm']
        if results['metrics'][task] != comparison['validation'][winner]:
            raise ValueError(f'{task} validation metrics differ from frozen historical evidence')
        historical_test[task] = comparison['test'][winner]
    verify_inventory(root, inventory)
    snapshot.mkdir(parents=True)
    for name in inventory:
        # Full reproducibility inputs, including data, remain local and untracked.
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
    verify_inventory(snapshot, inventory)
    write_new_json(output / 'inventory.json', inventory)
    write_new_json(output / 'baseline.json', results)
    write_new_json(output / 'historical-test.json', dict(
        status='already_exposed_historical_only_not_recomputed_or_used_for_selection', metrics=historical_test))
    receipt = dict(schema_version='ct1.1', created_at=datetime.now(timezone.utc).isoformat(),
        python=platform.python_version(), packages={p: version(p) for p in
            ['numpy', 'scipy', 'pandas', 'scikit-learn', 'joblib']},
        snapshot=str(snapshot.resolve()), protected_files=len(inventory),
        known_cases=len(cases), validation_rows=results['joint']['n_rows'],
        results_sha256=digest(output / 'baseline.json'), inventory_sha256=digest(output / 'inventory.json'),
        historical_test_sha256=digest(output / 'historical-test.json'),
        final_independent_dataset='not_yet_collected_or_human_reviewed')
    write_new_json(output / 'receipt.json', receipt)
    return receipt


def verify_baseline(root, output, snapshot):
    root, output, snapshot = Path(root), Path(output), Path(snapshot)
    receipt = read(output / 'receipt.json')
    for name, key in [('baseline.json', 'results_sha256'), ('inventory.json', 'inventory_sha256'),
                      ('historical-test.json', 'historical_test_sha256')]:
        if digest(output / name) != receipt[key]:
            raise ValueError(f'Baseline evidence changed: {name}')
    if receipt['python'] != platform.python_version() or any(
            version(p) != v for p, v in receipt['packages'].items()):
        raise ValueError('Baseline replay requires the recorded runtime')
    inventory = read(output / 'inventory.json')
    verify_inventory(root, inventory)
    verify_inventory(snapshot, inventory)
    from backend.model_service import ModelService
    service = ModelService(snapshot / 'models')
    if not service.loaded:
        raise ValueError(f'Invalid snapshot models: {service.status}')
    cases = read(snapshot / 'reports/quality/known-cases.json')['cases']
    replay = evaluate(snapshot, {t: getattr(service, t + '_model') for t in LABELS}, cases)
    if replay != read(output / 'baseline.json'):
        raise ValueError('Baseline replay differs')
    verify_inventory(root, inventory)
    verify_inventory(snapshot, inventory)
    return dict(verified=True, protected_files=len(inventory),
                validation_rows=replay['joint']['n_rows'], known_cases=len(cases))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['freeze', 'verify'])
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/evidence/ct1/baseline-v2')
    parser.add_argument('--snapshot', type=Path, default=ROOT / '.local-tools/ct1-baseline-v2')
    args = parser.parse_args()
    fn = create_baseline if args.action == 'freeze' else verify_baseline
    print(json.dumps(fn(ROOT, args.output, args.snapshot), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
