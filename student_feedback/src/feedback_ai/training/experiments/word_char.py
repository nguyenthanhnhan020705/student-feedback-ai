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
from feedback_ai.training.experiments.class_weights import class_weights, compare_results
CHAR_WEIGHTS = (.5, 1., 2.)

VARIANTS = {f'char_{weight:g}_{weighting}': dict(char_weight=weight, weighting=weighting)
            for weight in CHAR_WEIGHTS for weighting in ('none', 'ct2')}

ORDER = ('baseline', 'ct2', *VARIANTS)

def _pipeline(task, train, char_weight, weighting, ct2_selection):
    if (task not in LABELS or train.empty or not train['split'].eq('train').all()
            or any(not isinstance(t, str) or not t.strip() for t in train.text)
            or set(train[task]) != set(LABELS[task])):
        raise ValueError('Nonempty train with raw text and all canonical classes required')
    if char_weight not in CHAR_WEIGHTS or weighting not in ('none', 'ct2'):
        raise ValueError('Unknown CT3 fixed configuration')
    strategy = ct2_selection[task]
    weights = (None if weighting == 'none' or strategy == 'baseline'
               else class_weights(task, train[task].tolist(), strategy))
    features = FeatureUnion([
        ('word', TfidfVectorizer(preprocessor=normalize_text, **TFIDF_PARAMS)),
        ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=2,
            sublinear_tf=True, lowercase=False, preprocessor=normalize_text)),
    ], transformer_weights={'word': 1., 'char': float(char_weight)})
    params = {**CLF_PARAMS['linear_svm'], 'class_weight': weights}
    return Pipeline([('features', features), ('clf', LinearSVC(**params))])

def build_candidate(task, train, char_weight, weighting, ct2_selection):
    return _pipeline(task, train, char_weight, weighting, ct2_selection).fit(
        train.text.tolist(), train[task].tolist())

def select_candidate(metrics):
    if not metrics or set(metrics) - set(ORDER):
        raise ValueError('Unknown/empty candidate set')
    if any(type(m[k]) not in (int, float) or not math.isfinite(m[k])
           or not 0 <= m[k] <= 1 for m in metrics.values() for k in ('macro_f1', 'accuracy')):
        raise ValueError('Invalid selection scores')
    best_f1 = max(m['macro_f1'] for m in metrics.values())
    eligible = [n for n in ORDER if n in metrics and best_f1 - metrics[n]['macro_f1'] <= 1e-6]
    best_acc = max(metrics[n]['accuracy'] for n in eligible)
    return next(n for n in eligible if best_acc - metrics[n]['accuracy'] <= 1e-6)

def percentage_change(before, after):
    return dict(before_percent=100 * before, after_percent=100 * after,
        delta_percentage_points=100 * (after - before),
        relative_change_percent=100 * (after / before - 1) if before else None)

def _percent_comparison(before, after):
    return {**{task: {key: percentage_change(before['metrics'][task][key], after['metrics'][task][key])
                      for key in ('accuracy', 'macro_f1')} for task in LABELS},
            'joint': percentage_change(before['joint']['accuracy'], after['joint']['accuracy'])}
