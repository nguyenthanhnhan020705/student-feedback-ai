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
