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
from feedback_ai.training.experiments.class_weights import compare_results
from feedback_ai.training.experiments.word_char import percentage_change
RATIOS = (.25, .5, 1.)

VARIANTS = {f'{parent}_aug{int(ratio*100)}': dict(parent=parent, ratio=ratio)
            for parent in ('original', 'ct3parent') for ratio in RATIOS}

ORDER = ('original', 'ct2', 'ct3', *VARIANTS)

def augment_train(frame, ratio):
    if (ratio not in RATIOS or frame.empty or not frame.split.eq('train').all()
            or not frame.id.is_unique or any(not isinstance(t, str) or not t.strip() for t in frame.text)
            or any(set(frame[t]) != set(LABELS[t]) for t in LABELS)):
        raise ValueError('Require allowed ratio and nonempty unique train with canonical labels')
    rows = frame.to_dict('records')
    eligible = [r for r in rows if unaccent(r['text']) != r['text']]
    eligible.sort(key=lambda r: hashlib.sha256(f'ct4-v1|42|{r["id"]}'.encode()).hexdigest())
    added = [{**r, 'id': f'ct4-v1:{r["id"]}', 'parent_id': r['id'],
              'text': unaccent(r['text']), 'method': 'unaccent', 'version': 'ct4-v1', 'seed': 42}
             for r in eligible[:math.floor(ratio * len(eligible))]]
    if set(r['id'] for r in added) & set(frame.id):
        raise ValueError('Augmentation IDs collide with original source IDs')
    return pd.DataFrame(rows + [{k: r[k] for k in frame.columns} for r in added], columns=frame.columns), added

def collision_report(train, added, validation, cases):
    transformed = defaultdict(list)
    for row in train.to_dict('records'):
        transformed[normalize_text(unaccent(row['text']))].append(row)
    collisions = [dict(text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                       ids=[r['id'] for r in rows], labels=[{t:r[t] for t in LABELS} for r in rows])
                  for text, rows in sorted(transformed.items()) if len(rows) > 1]
    conflicts = [r for r in collisions if any(len({x[t] for x in r['labels']}) > 1 for t in LABELS)]
    source = train.to_dict('records')
    def overlaps(transform):
        indexes = defaultdict(list)
        for row in source + added:
            indexes[transform(row['text'])].append(row['id'])
        return {name: [dict(id=r['id'], train_ids=indexes[transform(r['text'])])
                       for r in rows if transform(r['text']) in indexes]
                for name, rows in [('validation', validation.to_dict('records')), ('known_cases', cases)]}
    return dict(source_groups=len(train), already_unaccented=sum(unaccent(t)==t for t in train.text),
        augmented_rows=len(added), transformed_collisions=collisions, conflicting_labels=conflicts,
        overlap_normalized=overlaps(normalize_text),
        overlap_unaccented=overlaps(lambda text: normalize_text(unaccent(text))),
        policy='report_only_no_filter_or_relabel', near_duplicates='not_certified')

def select_candidate(metrics):
    if not metrics or set(metrics) - set(ORDER):
        raise ValueError('Unknown/empty candidate set')
    if any(type(m[k]) not in (int,float) or not math.isfinite(m[k]) or not 0 <= m[k] <= 1
           for m in metrics.values() for k in ('macro_f1','accuracy')):
        raise ValueError('Invalid scores')
    top = max(m['macro_f1'] for m in metrics.values())
    eligible = [n for n in ORDER if n in metrics and top-metrics[n]['macro_f1'] <= 1e-6]
    acc = max(metrics[n]['accuracy'] for n in eligible)
    return next(n for n in eligible if acc-metrics[n]['accuracy'] <= 1e-6)

def fit_candidate(parent, train, task):
    if (task not in LABELS or train.empty or not train.split.eq('train').all()
            or set(train[task]) != set(LABELS[task])):
        raise ValueError('Only complete canonical train may be fitted')
    return clone(parent).fit(train.text.tolist(), train[task].tolist())

def _joint_transitions(before, after, validation):
    old, new = before['prediction_rows'], after['prediction_rows']
    if [r['id'] for r in old] != validation.id.tolist() or [r['id'] for r in new] != validation.id.tolist():
        raise ValueError('Joint alignment mismatch')
    truths = validation.to_dict('records')
    improved, regressed, changed = [], [], []
    for a,b,truth in zip(old,new,truths):
        oa = all(a[t]==truth[t] for t in LABELS)
        nb = all(b[t]==truth[t] for t in LABELS)
        if not oa and nb: improved.append(truth['id'])
        if oa and not nb: regressed.append(truth['id'])
        if any(a[t]!=b[t] for t in LABELS): changed.append(dict(id=truth['id'],before=a,after=b))
    return dict(improved=improved,regressed=regressed,changed=changed,scored=len(truths))

def comparison(before, after, validation):
    return dict(delta=compare_results(before,after,validation),
        joint_transitions=_joint_transitions(before,after,validation),
        percent={**{t:{k:percentage_change(before['metrics'][t][k],after['metrics'][t][k])
                       for k in ('accuracy','macro_precision','macro_recall','macro_f1')} for t in LABELS},
                 'joint':percentage_change(before['joint']['accuracy'],after['joint']['accuracy'])})
