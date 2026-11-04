"""CT2 train-only weighting experiments. Research artifacts never replace models/."""
from __future__ import annotations

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
from time import perf_counter
import warnings

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sklearn.base import clone
from sklearn.svm import LinearSVC

from reports.ct_evaluation import (
    LABELS, digest, read, write_new_json, verify_inventory, verify_baseline, evaluate,
)

STRATEGIES = ('sqrt_balanced', 'balanced', 'minority_x2')
ORDER = ('baseline', *STRATEGIES)
TOL = 1e-6


def class_weights(task, labels, strategy):
    if task not in LABELS or strategy not in STRATEGIES:
        raise ValueError('Unknown task or weighting strategy')
    counts = Counter(labels)
    if set(counts) != set(LABELS[task]):
        raise ValueError('Train must contain exactly the canonical classes')
    weights = {label: len(labels) / (len(counts) * counts[label]) for label in LABELS[task]}
    if strategy == 'sqrt_balanced':
        weights = {label: value ** .5 for label, value in weights.items()}
    elif strategy == 'minority_x2':
        minority = 'neutral' if task == 'sentiment' else 'other'
        weights = {label: 2.0 if label == minority else 1.0 for label in LABELS[task]}
    return weights


def fit_candidate(baseline, train, task, strategy):
    if train.empty or not train['split'].eq('train').all():
        raise ValueError('Only an unmixed nonempty train split may be fitted')
    if not isinstance(baseline.steps[-1][1], LinearSVC):
        raise ValueError('CT2 requires a LinearSVC baseline')
    weights = class_weights(task, train[task].tolist(), strategy)
    candidate = clone(baseline)
    candidate.set_params(**{candidate.steps[-1][0] + '__class_weight': weights})
    candidate.fit(train.text.tolist(), train[task].tolist())
    return candidate, weights


def select_candidate(metrics):
    if 'baseline' not in metrics or set(metrics) - set(ORDER):
        raise ValueError('Ranking requires baseline and known candidates')
    best_f1 = max(m['macro_f1'] for m in metrics.values())
    eligible = [name for name in ORDER if name in metrics
                and best_f1 - metrics[name]['macro_f1'] <= TOL]
    best_accuracy = max(metrics[name]['accuracy'] for name in eligible)
    return next(name for name in eligible
                if best_accuracy - metrics[name]['accuracy'] <= TOL)


def _transitions(before, after, truths, ids):
    changes, improved, regressed = [], [], []
    for rid, old, new, expected in zip(ids, before, after, truths):
        if old != new:
            changes.append(dict(id=rid, expected=expected, before=old, after=new))
        if expected is not None:
            if old == expected and new != expected:
                regressed.append(rid)
            elif old != expected and new == expected:
                improved.append(rid)
    return dict(scored=sum(t is not None for t in truths), changed=changes,
                improved=improved, regressed=regressed)


def compare_results(baseline, candidate, validation):
    ids = validation.id.tolist()
    if len(ids) != len(set(ids)) or any(
            [r['id'] for r in result['prediction_rows']] != ids
            for result in (baseline, candidate)):
        raise ValueError('Validation prediction alignment mismatch')
    left, right = baseline['known_cases']['rows'], candidate['known_cases']['rows']
    identity = lambda rows: [{k: r[k] for k in ('id', 'text', 'group', *LABELS)} for r in rows]
    if identity(left) != identity(right) or len({r['id'] for r in left}) != len(left):
        raise ValueError('Known-case alignment/expectations mismatch')
    result = dict(metrics={}, validation={}, known_cases={})
    for task, labels in LABELS.items():
        a, b = baseline['metrics'][task], candidate['metrics'][task]
        if a['label_order'] != labels or b['label_order'] != labels:
            raise ValueError('Metric class alignment mismatch')
        delta = {key: b[key] - a[key] for key in
                 ('accuracy', 'macro_precision', 'macro_recall', 'macro_f1')}
        delta['per_class'] = [dict(label=label, **{key: new[key] - old[key]
            for key in ('precision', 'recall', 'f1', 'support')})
            for label, old, new in zip(labels, a['per_class'], b['per_class'])]
        result['metrics'][task] = delta
        result['validation'][task] = _transitions(
            [r[task] for r in baseline['prediction_rows']],
            [r[task] for r in candidate['prediction_rows']], validation[task].tolist(), ids)
        result['known_cases'][task] = _transitions(
            [r['predicted'][task] for r in left], [r['predicted'][task] for r in right],
            [r[task] for r in left], [r['id'] for r in left])
    return result


def _locations(root, output, baseline_output, snapshot):
    root, output = Path(root).resolve(), Path(output).resolve()
    research = root / '.local-tools/ct2-class-weights'
    if output == research or not output.is_relative_to(research):
        raise ValueError('Use a fresh research output below .local-tools/ct2-class-weights/')
    baseline_output = Path(baseline_output or root / 'reports/evidence/ct1/baseline-v2').resolve()
    snapshot = Path(snapshot or root / '.local-tools/ct1-baseline-v2').resolve()
    for protected in (baseline_output, snapshot):
        if output.is_relative_to(protected) or protected.is_relative_to(output):
            raise ValueError('Research output overlaps frozen baseline')
    return root, output, baseline_output, snapshot


def _models(directory):
    from backend.model_service import ModelService
    service = ModelService(directory)
    if not service.loaded:
        raise ValueError(f'Both real model artifacts must be ready: {service.status}')
    return {task: getattr(service, task + '_model') for task in LABELS}


def _save_model(root, directory, task, pipeline, strategy, weights, metrics):
    directory.mkdir(parents=True, exist_ok=True)
    artifact = directory / f'{task}_pipeline.joblib'
    if artifact.exists():
        raise FileExistsError(f'Artifact already exists: {artifact}')
    metadata = copy.deepcopy(read(root / f'models/{task}_metadata.json'))
    joblib.dump(pipeline, artifact)
    metadata.update(artifact_sha256=digest(artifact),
                    trained_at=datetime.now(timezone.utc).isoformat())
    metadata['parameters']['classifier']['class_weight'] = weights
    metadata['selection']['validation_metrics'] = metrics
    metadata['ct2'] = dict(strategy=strategy, fit_split='train', deployment='research_only')
    write_new_json(directory / f'{task}_metadata.json', metadata)


def _check_model_parameters(directory, task, pipeline, baseline, weights, root):
    classifier = baseline.steps[-1][1]
    expected = {**classifier.get_params(deep=False), 'class_weight': weights}
    if (pipeline.steps[-1][1].get_params(deep=False) != expected
            or pipeline.named_steps['tfidf'].get_params(deep=False)
            != baseline.named_steps['tfidf'].get_params(deep=False)):
        raise ValueError('Candidate changed parameters outside class_weight')
    a, b = pipeline.named_steps['tfidf'], baseline.named_steps['tfidf']
    if a.vocabulary_ != b.vocabulary_ or not np.array_equal(a.idf_, b.idf_):
        raise ValueError('Candidate vocabulary/IDF differs from train-only baseline')
    metadata = read(directory / f'{task}_metadata.json')
    declared = copy.deepcopy(read(root / f'models/{task}_metadata.json')['parameters'])
    declared['classifier']['class_weight'] = weights
    if metadata['parameters'] != declared:
        raise ValueError('Candidate metadata parameters mismatch')


def _summary(results):
    lines = ['# CT2 — validation development results', '',
        'Class weighting only; historical test not evaluated. Serving models unchanged.', '',
        '| Task | Variant | Accuracy | Macro F1 | Delta Accuracy (pp) | Delta F1 (pp) |',
        '| --- | --- | ---: | ---: | ---: | ---: |']
    for task in LABELS:
        base = results['baseline']['metrics'][task]
        for name in ORDER:
            value = base if name == 'baseline' else results['candidates'][name]['evaluation']['metrics'][task]
            lines.append(f'| {task} | {name} | {value["accuracy"]:.4%} | {value["macro_f1"]:.4%}'
                         f' | {(value["accuracy"] - base["accuracy"])*100:+.4f}'
                         f' | {(value["macro_f1"] - base["macro_f1"])*100:+.4f} |')
    lines += ['', 'Validation rank leaders (research only): ' + str(results['selection']),
              '', 'Full per-class deltas and every changed/regressed ID: results.json.',
              'Known-case labels are assistant-proposed, not human-reviewed; null remains unscored.',
              'No independent final dataset; no deployment or broad quality claim.', '']
    return '\n'.join(lines)


def run_experiment(root, output, baseline_output=None, snapshot=None):
    root, output, baseline_output, snapshot = _locations(root, output, baseline_output, snapshot)
    if output.exists():
        raise FileExistsError(f'Research output already exists: {output}')
    verify_baseline(root, baseline_output, snapshot)
    from ml.data import load_split
    train = load_split(root / 'data/raw', 'train')
    validation = load_split(root / 'data/raw', 'validation')
    cases = read(root / 'reports/quality/known-cases.json')['cases']
    baseline_pipes = _models(root / 'models')
    baseline_result = read(baseline_output / 'baseline.json')
    # Exclusive directory claim; a failed run remains visibly incomplete (no receipt).
    output.mkdir(parents=True, exist_ok=False)
    config = dict(schema_version='ct2.1', strategies=list(STRATEGIES),
        fit_split='train', evaluation_split='validation', seed=42,
        train_rows=len(train), validation_rows=len(validation), known_cases=len(cases),
        train_counts={t: dict(Counter(train[t].tolist())) for t in LABELS},
        selection='global_validation_f1_band_then_global_accuracy_band_1e-6_baseline_first',
        promotion='not_deployed', test='historical_only_no_inference_or_selection')
    write_new_json(output / 'config.json', config)
    results = dict(config=config, baseline=baseline_result, candidates={}, promotion='not_deployed')
    for strategy in STRATEGIES:
        pipes, fit_records = {}, {}
        for task in LABELS:
            start = perf_counter()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                pipes[task], weights = fit_candidate(baseline_pipes[task], train, task, strategy)
            fit_records[task] = dict(class_weight=weights, seconds=perf_counter() - start,
                warnings=[dict(category=w.category.__name__, message=str(w.message)) for w in caught])
        scored = evaluate(root, pipes, cases)
        path = output / 'candidates' / strategy
        for task in LABELS:
            _save_model(root, path, task, pipes[task], strategy,
                        fit_records[task]['class_weight'], scored['metrics'][task])
        loaded = _models(path)
        for task in LABELS:
            _check_model_parameters(path, task, loaded[task], baseline_pipes[task],
                                    fit_records[task]['class_weight'], root)
        if evaluate(root, loaded, cases) != scored:
            raise ValueError('Serialized candidate differs from fitted pipeline')
        results['candidates'][strategy] = dict(fit=fit_records, evaluation=scored,
            delta_vs_baseline=compare_results(baseline_result, scored, validation))
        print(f'Fitted and verified {strategy}', flush=True)
    results['selection'] = {task: select_candidate({
        'baseline': baseline_result['metrics'][task],
        **{name: item['evaluation']['metrics'][task] for name, item in results['candidates'].items()}})
        for task in LABELS}
    selected = output / 'research-selected'
    selected.mkdir()
    for task, name in results['selection'].items():
        source = root / 'models' if name == 'baseline' else output / 'candidates' / name
        for suffix in ('pipeline.joblib', 'metadata.json'):
            shutil.copyfile(source / f'{task}_{suffix}', selected / f'{task}_{suffix}')
    combined = evaluate(root, _models(selected), cases)
    results['research_selected'] = dict(evaluation=combined,
        delta_vs_baseline=compare_results(baseline_result, combined, validation))
    write_new_json(output / 'results.json', results)
    (output / 'summary.md').write_text(_summary(results), encoding='utf-8')
    verify_inventory(root, read(baseline_output / 'inventory.json'))
    payload = {p.relative_to(output).as_posix(): digest(p) for p in sorted(output.rglob('*')) if p.is_file()}
    receipt = dict(schema_version='ct2.1', completed_at=datetime.now(timezone.utc).isoformat(),
        runtime=read(baseline_output / 'receipt.json'), code_sha256=digest(Path(__file__)),
        baseline_receipt_sha256=digest(baseline_output / 'receipt.json'),
        payload=payload, selection=results['selection'], promotion='not_deployed')
    write_new_json(output / 'receipt.json', receipt)
    return dict(output=str(output), selection=results['selection'], promotion='not_deployed')


def verify_experiment(root, output, baseline_output=None, snapshot=None):
    root, output, baseline_output, snapshot = _locations(root, output, baseline_output, snapshot)
    receipt = read(output / 'receipt.json')
    if (receipt['code_sha256'] != digest(Path(__file__))
            or receipt['baseline_receipt_sha256'] != digest(baseline_output / 'receipt.json')):
        raise ValueError('CT2 runner or baseline evidence changed')
    verify_inventory(output, receipt['payload'])
    verify_baseline(root, baseline_output, snapshot)
    from ml.data import load_split
    train = load_split(root / 'data/raw', 'train')
    validation = load_split(root / 'data/raw', 'validation')
    cases = read(root / 'reports/quality/known-cases.json')['cases']
    results = read(output / 'results.json')
    if results['baseline'] != read(baseline_output / 'baseline.json'):
        raise ValueError('CT2 baseline differs from CT1')
    base = _models(root / 'models')
    for name in STRATEGIES:
        directory = output / 'candidates' / name
        pipes = _models(directory)
        stored = results['candidates'][name]
        for task in LABELS:
            weights = class_weights(task, train[task].tolist(), name)
            _check_model_parameters(directory, task, pipes[task], base[task], weights, root)
            if stored['fit'][task]['class_weight'] != weights:
                raise ValueError('Recorded train weights differ')
        actual = evaluate(root, pipes, cases)
        if (actual != stored['evaluation'] or compare_results(results['baseline'], actual, validation)
                != stored['delta_vs_baseline']):
            raise ValueError('Replayed candidate metrics/regressions differ')
    selection = {task: select_candidate({'baseline': results['baseline']['metrics'][task],
        **{name: results['candidates'][name]['evaluation']['metrics'][task] for name in STRATEGIES}})
        for task in LABELS}
    if selection != results['selection'] or selection != receipt['selection']:
        raise ValueError('Validation selection differs')
    for task, name in selection.items():
        source = root / 'models' if name == 'baseline' else output / 'candidates' / name
        for suffix in ('pipeline.joblib', 'metadata.json'):
            filename = f'{task}_{suffix}'
            if digest(source / filename) != digest(output / 'research-selected' / filename):
                raise ValueError('Combined research selection differs')
    combined = evaluate(root, _models(output / 'research-selected'), cases)
    if results['research_selected'] != dict(evaluation=combined,
            delta_vs_baseline=compare_results(results['baseline'], combined, validation)):
        raise ValueError('Combined research evaluation differs')
    verify_inventory(root, read(baseline_output / 'inventory.json'))
    return dict(verified=True, candidates=len(STRATEGIES) * len(LABELS),
                selection=selection, promotion='not_deployed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', 'verify'))
    parser.add_argument('--output', type=Path, default=ROOT / '.local-tools/ct2-class-weights/run-2')
    args = parser.parse_args()
    fn = run_experiment if args.action == 'run' else verify_experiment
    import json
    print(json.dumps(fn(ROOT, args.output), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
