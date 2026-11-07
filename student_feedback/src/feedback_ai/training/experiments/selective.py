import hashlib
import math
import copy
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from feedback_ai.data.preprocessing import normalize_text
from feedback_ai.data.transforms import unaccent
from feedback_ai.common.labels import SENTIMENT_LABELS, TOPIC_LABELS
from feedback_ai.training.sentiment import TFIDF_PARAMS, CLF_PARAMS
from feedback_ai.evaluation.metrics import score_labels
LABELS={'sentiment':list(SENTIMENT_LABELS),'topic':list(TOPIC_LABELS)}
QUANTILES = {'zero_plus_margin_q05': .05, 'zero_plus_margin_q10': .10,
             'zero_plus_margin_q20': .20}

POLICIES = ('always_answer', 'zero_features', *QUANTILES)

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
