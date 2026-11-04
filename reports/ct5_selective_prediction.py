"""CT5 milestone A: frozen, read-only selective prediction; no serving changes."""
from __future__ import annotations

import hashlib
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys

import numpy as np
from scipy import sparse
from sklearn.pipeline import FeatureUnion, Pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.preprocessing import normalize_text
from reports.ct_evaluation import LABELS, score_labels, digest, read, write_new_json, verify_inventory
from reports.ct4_augmentation import unaccent

QUANTILES = {'zero_plus_margin_q05': .05, 'zero_plus_margin_q10': .10,
             'zero_plus_margin_q20': .20}
POLICIES = ('always_answer', 'zero_features', *QUANTILES)


def _nnz(matrix):
    if sparse.issparse(matrix):
        result = matrix.tocsr(copy=True)
        result.eliminate_zeros()
        if not np.isfinite(result.data).all():
            raise ValueError('Nonfinite feature values')
        return result.getnnz(axis=1).astype(int).tolist()
    array = np.asarray(matrix)
    if array.ndim != 2 or not np.isfinite(array).all():
        raise ValueError('Invalid feature matrix')
    return np.count_nonzero(array, axis=1).astype(int).tolist()


def extract_signals(pipeline, texts, task):
    """Use actual multiclass columns and the complete pre-classifier transform."""
    if task not in LABELS or not isinstance(pipeline, Pipeline) or len(pipeline.steps) < 2:
        raise ValueError('Expected task and fitted feature/classifier pipeline')
    if not isinstance(texts, list) or any(not isinstance(t, str) or not t.strip() for t in texts):
        raise ValueError('Expected nonblank raw strings')
    classes = list(pipeline.classes_)
    if (len(classes) != len(LABELS[task]) or set(classes) != set(LABELS[task])):
        raise ValueError('Invalid classifier classes')
    if not texts:
        return []
    transform = pipeline[:-1]
    features = transform.transform(texts)
    counts = _nnz(features)
    clf = pipeline.steps[-1][1]
    scores = np.asarray(clf.decision_function(features))
    if scores.shape != (len(texts), len(classes)) or not np.isfinite(scores).all():
        raise ValueError('Invalid/nonfinite score shape')
    predicted = list(pipeline.predict(texts))
    expected = [classes[i] for i in scores.argmax(axis=1)]
    if predicted != expected:
        raise ValueError('Prediction does not agree with actual class score columns')
    branches = {}
    # CT3 features use a FeatureUnion as the final feature transformer.
    last = pipeline.steps[-2][1]
    if isinstance(last, FeatureUnion):
        inputs = pipeline[:-2].transform(texts) if len(pipeline.steps) > 2 else texts
        weights = last.transformer_weights or {}
        for name, branch in last.transformer_list:
            if branch == 'drop':
                continue
            values = inputs if branch == 'passthrough' else branch.transform(inputs)
            branches[name] = _nnz(values * weights.get(name, 1.))
    else:
        branches[pipeline.steps[-2][0]] = counts
    ordered = np.sort(scores, axis=1)
    gaps = ordered[:, -1] - ordered[:, -2]
    return [dict(prediction=str(predicted[i]), classes=classes,
                 scores=scores[i].tolist(), gap=float(gaps[i]), nnz=counts[i],
                 branch_nnz={name: values[i] for name, values in branches.items()})
            for i in range(len(texts))]


def partition_validation(frame):
    if not frame.id.is_unique:
        raise ValueError('Duplicate validation IDs')
    rows = []
    for row in frame.to_dict('records'):
        key = normalize_text(unaccent(row['text']))
        digest = hashlib.sha256(('ct5-v1|42|' + key).encode('utf-8')).hexdigest()
        rows.append(dict(id=row['id'], group_key=key, group_digest=digest,
                         source_group=digest,
                         subset='threshold_development' if int(digest[:2], 16) < 128 else 'policy_audit'))
    sizes = {name: sum(r['subset'] == name for r in rows)
             for name in ('threshold_development', 'policy_audit')}
    return dict(rows=rows, counts=sizes,
                status='available' if all(sizes.values()) else 'insufficient_partition',
                independence='both_subsets_are_repeatedly_exposed_validation')


def fit_thresholds(signals, indices):
    """No classifier fitting: frozen quantiles of nonzero development gaps only."""
    result = {name: {} for name in QUANTILES}
    for task in LABELS:
        values = [signals[task][i]['gap'] for i in indices if signals[task][i]['nnz'] > 0]
        if not np.isfinite(values).all():
            raise ValueError('Nonfinite development gaps')
        for name, q in QUANTILES.items():
            result[name][task] = float(np.quantile(values, q, method='linear')) if values else None
    return result


def apply_policy(rows, signals, policy, thresholds):
    if policy not in POLICIES or any(len(signals[t]) != len(rows) for t in LABELS):
        raise ValueError('Unknown policy or misaligned signals')
    if policy in QUANTILES and any(thresholds.get(policy, {}).get(t) is None for t in LABELS):
        raise ValueError('Cannot apply margin policy without development threshold')
    result = []
    for i, row in enumerate(rows):
        accepted, raw, reasons, diagnostic = {}, {}, [], {}
        for task in LABELS:
            s = signals[task][i]
            if s['prediction'] not in LABELS[task]:
                raise ValueError('Invalid prediction label')
            threshold = thresholds[policy][task] if policy in QUANTILES else None
            task_reasons = []
            if policy != 'always_answer' and s['nnz'] == 0:
                task_reasons.append('zero_features_' + task)
            if policy in QUANTILES and s['gap'] < threshold:
                task_reasons.append('low_margin_' + task)
            reasons.extend(task_reasons)
            accepted[task] = not task_reasons
            raw[task] = s['prediction']
            diagnostic[task] = {**s, 'threshold': threshold}
        pair = all(accepted.values())
        result.append(dict(id=row['id'], source_group=row.get('source_group'),
            source=row.get('source'), group=row.get('group'),
            label_provenance=row.get('label_provenance'),
            truth={t: row.get(t) for t in LABELS}, answerability=row.get('answerability'),
            raw_prediction=raw, signals=diagnostic, accepted=accepted, accepted_pair=pair,
            reasons=reasons, labels_for_display=raw.copy() if pair else None))
    return result


def _ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def _metrics(rows, task):
    labeled = [r for r in rows if r['truth'][task] is not None]
    return score_labels([r['truth'][task] for r in labeled],
                        [r['raw_prediction'][task] for r in labeled], LABELS[task]) if labeled else None


def _answerability(decisions):
    result = {}
    for unit in (*LABELS, 'pair'):
        categories = {'answerable': [], 'unanswerable': [], 'ambiguous': [], 'missing': []}
        for row in decisions:
            values = [(row.get('answerability') or {}).get(t) for t in LABELS]
            if unit != 'pair':
                value = (row.get('answerability') or {}).get(unit)
            elif any(v is None for v in values):
                value = None
            elif 'unanswerable' in values:
                value = 'unanswerable'
            elif 'ambiguous' in values:
                value = 'ambiguous'
            else:
                value = 'answerable'
            if value not in ('answerable', 'unanswerable', 'ambiguous', None):
                raise ValueError('Invalid answerability category')
            categories[value or 'missing'].append(row)
        def accepts(row):
            return row['accepted_pair'] if unit == 'pair' else row['accepted'][unit]
        answerable, unanswerable = categories['answerable'], categories['unanswerable']
        rejected_answerable = sum(not accepts(r) for r in answerable)
        rejected_unanswerable = sum(not accepts(r) for r in unanswerable)
        accepted_answerable = [r for r in answerable if accepts(r)]
        if unit == 'pair':
            labeled = [r for r in accepted_answerable if all(r['truth'][t] is not None for t in LABELS)]
            correct = sum(all(r['truth'][t] == r['raw_prediction'][t] for t in LABELS) for r in labeled)
            metrics = dict(n_rows=len(labeled), accuracy=_ratio(correct, len(labeled)))
        else:
            metrics = _metrics(accepted_answerable, unit)
        result[unit] = dict(**{k: len(v) for k, v in categories.items()},
            rejected_answerable=rejected_answerable, accepted_unanswerable=len(unanswerable)-rejected_unanswerable,
            false_reject_rate=_ratio(rejected_answerable, len(answerable)),
            unsafe_accept_rate=_ratio(len(unanswerable)-rejected_unanswerable, len(unanswerable)),
            precision_of_abstention=_ratio(rejected_unanswerable, rejected_answerable+rejected_unanswerable),
            accepted_answerable_metrics=metrics)
    result['status'] = 'provided_labels_review_provenance_required' if any(r.get('answerability') for r in decisions) else 'no_reviewed_answerability'
    return result


def summarize(decisions):
    n = len(decisions)
    accepted = [r for r in decisions if r['accepted_pair']]
    labeled = [r for r in decisions if all(r['truth'][t] is not None for t in LABELS)]
    counts = dict(correct_answered=0, wrong_answered=0, rejected_correct=0, rejected_wrong=0)
    for row in labeled:
        correct = all(row['truth'][t] == row['raw_prediction'][t] for t in LABELS)
        key = ('correct_answered' if correct else 'wrong_answered') if row['accepted_pair'] else ('rejected_correct' if correct else 'rejected_wrong')
        counts[key] += 1
    c, e = counts['correct_answered'], counts['wrong_answered']
    joint = dict(**counts, n_labeled=len(labeled), accepted_labeled=c+e,
        correctness_denominator='inputs_with_both_truth_labels',
        accepted_accuracy=_ratio(c, c+e), selective_risk=_ratio(e, c+e),
        correct_and_answered_rate=_ratio(c, len(labeled)), answered_wrong_rate=_ratio(e, len(labeled)),
        rejected_correct_rate=_ratio(counts['rejected_correct'], len(labeled)),
        rejected_wrong_rate=_ratio(counts['rejected_wrong'], len(labeled)))
    tasks = {}
    for task in LABELS:
        task_accepted = [r for r in decisions if r['accepted'][task]]
        tasks[task] = dict(accepted_count=len(task_accepted), coverage=_ratio(len(task_accepted), n),
            n_labeled=sum(r['truth'][task] is not None for r in decisions),
            ungated_metrics=_metrics(decisions, task), accepted_metrics=_metrics(task_accepted, task),
            pair_accepted_metrics=_metrics(accepted, task))
    return dict(input_count=n, accepted_pair_count=len(accepted), rejected_pair_count=n-len(accepted),
        pair_coverage=_ratio(len(accepted), n), abstention_rate=_ratio(n-len(accepted), n),
        joint=joint, tasks=tasks, answerability=_answerability(decisions),
        reason_counts={reason: sum(reason in r['reasons'] for r in decisions)
                       for reason in sorted({reason for r in decisions for reason in r['reasons']})})


def _locations(root, output, ct4_output):
    root = Path(root).resolve()
    research = root / '.local-tools/ct5-selective-prediction'
    output = Path(output).absolute()
    ct4 = Path(ct4_output or root/'.local-tools/ct4-augmentation/run-1').absolute()
    for path in (root/'.local-tools', research, output, ct4):
        if path.resolve() != path:
            raise ValueError('Redirected or noncanonical research path')
    if output == research or not output.is_relative_to(research):
        raise ValueError('Use a fresh output below .local-tools/ct5-selective-prediction/')
    ct4_base = root/'.local-tools/ct4-augmentation'
    if not ct4.is_relative_to(ct4_base) or ct4 == ct4_base:
        raise ValueError('CT4 control must be a research run')
    if output.is_relative_to(ct4) or ct4.is_relative_to(output):
        raise ValueError('Research output overlaps control')
    return root, output, ct4


def _runtime():
    return dict(python=platform.python_version(),
        packages={p: version(p) for p in ['numpy','scipy','pandas','scikit-learn','joblib']})


def _source_hashes():
    # Bind executable dependencies and the governing documents, not generated reports.
    names = ['reports/ct5_selective_prediction.py', 'reports/ct_evaluation.py',
        'reports/ct2_class_weights.py', 'reports/ct3_word_char.py', 'reports/ct4_augmentation.py',
        'ml/data.py', 'ml/preprocessing.py', 'ml/labels.py', 'backend/model_service.py',
        'backend/config.py', 'docs/quality/ct1-protocol.md', 'docs/quality/ct5-agent-handoff.md',
        'docs/specs/api-contract.md', 'docs/specs/data-contract.md']
    return {name: digest(ROOT/name) for name in names}


def _controls(root, ct4):
    from reports.ct4_augmentation import verify_experiment, _models
    verify_experiment(root, ct4)
    directories = {'original': root/'models', 'ct4': ct4/'research-selected'}
    models = {name: _models(path) for name, path in directories.items()}
    return directories, models


def _configuration(root, ct4, directories):
    from ml.data import _paths
    parents = {name: {f'{task}_{suffix}': digest(path/f'{task}_{suffix}')
                     for task in LABELS for suffix in ('pipeline.joblib','metadata.json')}
               for name, path in directories.items()}
    controls = {'ct1': root/'reports/evidence/ct1/baseline-v2/receipt.json',
                'ct2': root/'.local-tools/ct2-class-weights/run-2/receipt.json',
                'ct3': root/'.local-tools/ct3-word-char/run-1/receipt.json', 'ct4': ct4/'receipt.json'}
    return dict(schema_version='ct5.1', policies=list(POLICIES), quantiles=QUANTILES,
        quantile_method='linear', threshold_rows='nonzero_threshold_development_only',
        partition="SHA256('ct5-v1|42|'+normalize_text(unaccent(text))); first byte <128 development",
        runtime=_runtime(), source_hashes=_source_hashes(), models=parents,
        control_receipts={name: digest(path) for name, path in controls.items()},
        source_data={p.relative_to(root).as_posix(): digest(p)
                     for split in ('train','validation') for p in _paths(root/'data/raw', split)},
        manifest_sha256=digest(root/'reports/data/manifest.json'),
        known_labels_sha256=digest(root/'reports/quality/known-cases.json'),
        classifier_fit=False, test='no_inference_or_threshold_selection',
        promotion='not_deployed', deployment='offline_research_only',
        recommended_policy=None, decision_status='needs_coverage_risk_decision')


def _data_status():
    return dict(status='engineering_complete_independent_evaluation_pending',
        independent_final_set='not_available', human_reviewed_answerability='not_available',
        semantic_false_reject=None, semantic_unsafe_accept=None,
        missing=['independent naturally sampled feedback with permission',
                 'two independent reviewers and resolved disagreements',
                 'task answerability labels and reviewer/source provenance',
                 'development/final source-group separation and duplicate audit',
                 'user coverage/risk decision before deployment proposal'],
        validation='repeatedly_exposed_development_only',
        known='assistant_proposed_not_human_reviewed', stress='synthetic_inherited_labels_not_independent',
        recommended_policy=None, decision_status='needs_coverage_risk_decision',
        promotion='not_deployed', deployment='offline_research_only', source_license='unknown')


def _overlap_audit(train, validation, ct4):
    groups = defaultdict(list)
    train_groups = defaultdict(list)
    augmentation = defaultdict(list)
    for row in train.to_dict('records'):
        train_groups[normalize_text(unaccent(row['text']))].append(row['id'])
    # Read the frozen augmented lineage for each selected task; no re-augmentation/fit.
    selection = read(ct4/'results.json')['selection']
    for task, name in selection.items():
        if '_aug' in name:
            ratio = int(name.rsplit('_aug', 1)[1])
            for row in read(ct4/f'augmentation/{ratio}.json')['added']:
                augmentation[normalize_text(unaccent(row['text']))].append(dict(task=task, parent_id=row['parent_id']))
    for row in validation.to_dict('records'):
        groups[normalize_text(unaccent(row['text']))].append(row)
    conflicts, overlap = [], []
    for key, rows in sorted(groups.items()):
        group = hashlib.sha256(('ct5-v1|42|' + key).encode()).hexdigest()
        if any(len({r[t] for r in rows}) > 1 for t in LABELS):
            conflicts.append(dict(source_group=group, ids=[r['id'] for r in rows],
                                  labels=[{t: r[t] for t in LABELS} for r in rows]))
        if key in train_groups or key in augmentation:
            overlap.append(dict(source_group=group, validation_ids=[r['id'] for r in rows],
                train_ids=train_groups.get(key, []), selected_augmentation=augmentation.get(key, [])))
    return dict(conflicting_validation_groups=conflicts, train_augmentation_overlap=overlap,
        overlap_validation_rows=sum(len(r['validation_ids']) for r in overlap),
        policy='report_only_no_filter_relabel_or_resplit', near_duplicates='not_certified')


def _dataset_rows(frame, source, provenance):
    return [dict(row, source=source, source_group=hashlib.sha256(
        ('ct5-v1|42|' + normalize_text(unaccent(row['text']))).encode()).hexdigest(),
        label_provenance=provenance) for row in frame.to_dict('records')]


def _evaluate_payloads(root, ct4, config, models):
    from ml.data import load_split
    train = load_split(root/'data/raw', 'train')
    validation = load_split(root/'data/raw', 'validation')
    partition = partition_validation(validation)
    partition['label_counts'] = {subset: {task: dict(Counter(
        validation.iloc[[i for i, r in enumerate(partition['rows']) if r['subset'] == subset]][task]))
        for task in LABELS} for subset in partition['counts']}
    partition['group_counts'] = {subset: len({r['source_group'] for r in partition['rows'] if r['subset'] == subset})
                                 for subset in partition['counts']}
    partition['overlap_audit'] = _overlap_audit(train, validation, ct4)
    full = _dataset_rows(validation, 'official_validation_repeatedly_exposed', 'UIT-VSFC_official_labels')
    indices = {subset: [i for i, row in enumerate(partition['rows']) if row['subset'] == subset]
               for subset in partition['counts']}
    cases = read(root/'reports/quality/known-cases.json')['cases']
    known = [dict(row, source='known_exposed', source_group=hashlib.sha256(
        ('ct5-v1|42|' + normalize_text(unaccent(row['text']))).encode()).hexdigest()) for row in cases]
    stress = [dict(row, text=unaccent(row['text']), source='synthetic_unaccented_validation',
                   label_provenance='inherited_weak_supervision_not_human_reviewed') for row in full]
    thresholds, decisions, metrics, full_metrics = {}, {}, {}, {}
    for pair, pipelines in models.items():
        signals = {t: extract_signals(pipelines[t], [r['text'] for r in full], t) for t in LABELS}
        thresholds[pair] = fit_thresholds(signals, indices['threshold_development'])
        datasets = {name: ([full[i] for i in selected], {t: [signals[t][i] for i in selected] for t in LABELS})
                    for name, selected in indices.items()}
        for name, rows in [('known', known), ('stress_unaccented_validation', stress)]:
            datasets[name] = (rows, {t: extract_signals(pipelines[t], [r['text'] for r in rows], t) for t in LABELS})
        decisions[pair], metrics[pair] = {}, {}
        full_decisions = apply_policy(full, signals, 'always_answer', {})
        full_metrics[pair] = summarize(full_decisions)
        for dataset, (rows, data_signals) in datasets.items():
            decisions[pair][dataset], metrics[pair][dataset] = {}, {}
            for policy in POLICIES:
                unavailable = policy in QUANTILES and any(thresholds[pair][policy][t] is None for t in LABELS)
                if unavailable:
                    decisions[pair][dataset][policy] = None
                    metrics[pair][dataset][policy] = dict(status='threshold_unavailable', input_count=len(rows))
                    continue
                actual = apply_policy(rows, data_signals, policy, thresholds[pair])
                scored = summarize(actual)
                scored['groups'] = {group: summarize([r for r in actual if r['group'] == group])
                                    for group in sorted({r['group'] for r in actual if r['group'] is not None})}
                decisions[pair][dataset][policy], metrics[pair][dataset][policy] = actual, scored
        # Same-model gating cannot create extra correctly answered inputs.
        for dataset in metrics[pair].values():
            baseline = dataset['always_answer']['joint']['correct_answered']
            for m in dataset.values():
                if 'joint' in m and m['joint']['correct_answered'] > baseline:
                    raise ValueError('Gate inflated correct answers')
    return {'config.json': config, 'partition.json': partition, 'thresholds.json': thresholds,
            'decisions.json': decisions, 'metrics.json': metrics, 'ungated-full-validation.json': full_metrics,
            'data-status.json': _data_status()}


def _summary(payloads):
    lines = ['# CT5 offline development — no policy recommended', '',
        'Both partitions are exposed validation; margin is not probability. Rejected inputs are not correct.', '',
        '| Pair / policy (same policy-audit IDs) | N | A | C | E | Coverage | Accepted accuracy | Risk | C/N |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    def fmt(value):
        return 'null' if value is None else f'{100*value:.4f}%'
    for pair, datasets in payloads['metrics.json'].items():
        for policy, m in datasets['policy_audit'].items():
            if 'joint' not in m:
                lines.append(f'| {pair}/{policy} | threshold unavailable | | | | | | | |')
                continue
            j = m['joint']
            lines.append(f"| {pair}/{policy} | {m['input_count']} | {m['accepted_pair_count']} | {j['correct_answered']} | {j['wrong_answered']} | {fmt(m['pair_coverage'])} | {fmt(j['accepted_accuracy'])} | {fmt(j['selective_risk'])} | {fmt(j['correct_and_answered_rate'])} |")
    lines += ['', 'Status: engineering_complete_independent_evaluation_pending.',
              'Decision: needs_coverage_risk_decision; recommended_policy=null; not_deployed.', '']
    return '\n'.join(lines)


def _payload_members(output):
    result = {}
    for path in sorted(output.rglob('*')):
        if path.resolve() != path:
            raise ValueError('Redirected payload path')
        if path.is_file() and path != output/'receipt.json':
            result[path.relative_to(output).as_posix()] = digest(path)
    return result


def run_experiment(root, output, ct4_output=None):
    root, output, ct4 = _locations(root, output, ct4_output)
    if output.exists():
        raise FileExistsError('Research output already exists')
    directories, models = _controls(root, ct4)
    config = _configuration(root, ct4, directories)
    # Frozen before scoring. Partial runs never receive a completion receipt.
    output.mkdir(parents=True, exist_ok=False)
    write_new_json(output/'config.json', config)
    payloads = _evaluate_payloads(root, ct4, config, models)
    if config != _configuration(root, ct4, directories):
        raise ValueError('Control inputs changed during evaluation')
    for name, value in payloads.items():
        if name != 'config.json':
            write_new_json(output/name, value)
    (output/'summary.md').write_text(_summary(payloads), encoding='utf-8')
    write_new_json(output/'receipt.json', dict(schema_version='ct5.1',
        promotion='not_deployed', deployment='offline_research_only', recommended_policy=None,
        decision_status='needs_coverage_risk_decision', status=_data_status()['status'],
        completed_at=datetime.now(timezone.utc).isoformat(), runtime=_runtime(),
        source_hashes=_source_hashes(), config_sha256=digest(output/'config.json'),
        payload=_payload_members(output)))
    return dict(output=str(output), status=_data_status()['status'], promotion='not_deployed')


def verify_experiment(root, output, ct4_output=None):
    root, output, ct4 = _locations(root, output, ct4_output)
    receipt = read(output/'receipt.json')
    expected = dict(schema_version='ct5.1', promotion='not_deployed', deployment='offline_research_only',
        recommended_policy=None, decision_status='needs_coverage_risk_decision', status=_data_status()['status'],
        runtime=_runtime(), source_hashes=_source_hashes(), config_sha256=digest(output/'config.json'))
    if any(key not in receipt or receipt[key] != value for key, value in expected.items()):
        raise ValueError('Receipt semantics, source or runtime changed')
    try:
        timestamp = datetime.fromisoformat(receipt['completed_at'])
        if timestamp.utcoffset() != timezone.utc.utcoffset(timestamp):
            raise ValueError('Receipt timestamp must be UTC')
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError('Invalid completion timestamp') from exc
    for name in receipt['payload']:
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or not (output/path).resolve().is_relative_to(output):
            raise ValueError('Unsafe receipt payload path')
    if receipt['payload'] != _payload_members(output):
        raise ValueError('Receipt payload hashes or exact membership differ')
    directories, models = _controls(root, ct4)
    config = _configuration(root, ct4, directories)
    actual = _evaluate_payloads(root, ct4, config, models)
    expected_names = set(actual) | {'summary.md'}
    if set(receipt['payload']) != expected_names:
        raise ValueError('Unexpected payload membership')
    for name, value in actual.items():
        if read(output/name) != value:
            raise ValueError('Replayed payload differs: ' + name)
    if (output/'summary.md').read_text(encoding='utf-8') != _summary(actual):
        raise ValueError('Replayed summary differs')
    if config != _configuration(root, ct4, directories):
        raise ValueError('Control inputs changed during replay')
    return dict(verified=True, policies_per_pair=5, pairs=2, fit=False,
                status=_data_status()['status'], promotion='not_deployed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run','verify'))
    parser.add_argument('--output', type=Path, default=ROOT/'.local-tools/ct5-selective-prediction/run-1')
    args = parser.parse_args()
    print(json.dumps((run_experiment if args.action == 'run' else verify_experiment)(ROOT, args.output), indent=2))


if __name__ == '__main__':
    main()
