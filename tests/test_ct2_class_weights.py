"""Protect train-only experiments, honest regressions and frozen serving models."""
import copy
import math

import pandas as pd
import pytest

from reports.ct_evaluation import score_labels, score_cases
from reports.ct2_class_weights import (
    class_weights, fit_candidate, select_candidate, compare_results,
)
from ml.train_sentiment import train_models


def test_weights_derive_from_train_counts_not_validation():
    y = ['negative'] * 6 + ['neutral'] * 2 + ['positive'] * 4
    assert class_weights('sentiment', y, 'balanced') == {
        'negative': 2 / 3, 'neutral': 2, 'positive': 1}
    assert class_weights('sentiment', y, 'sqrt_balanced') == {
        'negative': math.sqrt(2 / 3), 'neutral': math.sqrt(2), 'positive': 1}
    assert class_weights('sentiment', y, 'minority_x2') == {
        'negative': 1, 'neutral': 2, 'positive': 1}
    assert class_weights('topic', ['lecturer', 'curriculum', 'facility', 'other'],
                         'minority_x2')['other'] == 2


@pytest.mark.parametrize('y', [[], ['negative'], ['negative', 'neutral', 'positive', 'bad']])
def test_weights_reject_missing_or_unknown_classes(y):
    with pytest.raises(ValueError):
        class_weights('sentiment', y, 'balanced')


def training_frame(split='train'):
    return pd.DataFrame([
        dict(id=f'{split}:{i}', text=text, sentiment=label, topic='lecturer', split=split)
        for i, (text, label) in enumerate([
            ('bad poor course', 'negative'), ('bad poor teacher', 'negative'),
            ('ordinary normal course', 'neutral'), ('ordinary normal teacher', 'neutral'),
            ('great excellent course', 'positive'), ('great excellent teacher', 'positive')])])


def test_fit_preserves_baseline_and_fits_only_supplied_train_vocabulary():
    frame = training_frame()
    baseline = train_models(frame)['linear_svm']
    before = baseline.predict(frame.text.tolist()).tolist()
    params = baseline.steps[-1][1].get_params()
    candidate, weights = fit_candidate(baseline, frame, 'sentiment', 'minority_x2')
    assert baseline.steps[-1][1].class_weight is None
    assert baseline.predict(frame.text.tolist()).tolist() == before
    assert candidate.steps[-1][1].get_params() == {**params, 'class_weight': weights}
    candidate.predict(['validationonlyword'])
    assert 'validationonlyword' not in candidate.named_steps['tfidf'].vocabulary_


def test_fit_rejects_validation_even_if_it_has_all_labels():
    baseline = train_models(training_frame())['linear_svm']
    with pytest.raises(ValueError, match='train'):
        fit_candidate(baseline, training_frame('validation'), 'sentiment', 'balanced')


@pytest.mark.parametrize('metrics,winner', [
    ({'baseline': (.75, .92), 'balanced': (.76, .90)}, 'balanced'),
    ({'baseline': (.75, .92), 'balanced': (.7500005, .92)}, 'baseline'),
    ({'baseline': (.75, .92), 'balanced': (.7500005, .93)}, 'balanced'),
    ({'baseline': (.80, .92), 'balanced': (.79, .99)}, 'baseline'),
])
def test_selection_uses_validation_macro_f1_then_accuracy_then_baseline(metrics, winner):
    values = {k: dict(macro_f1=f1, accuracy=acc) for k, (f1, acc) in metrics.items()}
    assert select_candidate(values) == winner


def test_selection_does_not_chain_ties_below_global_best_macro_f1():
    # Each step is within 1e-6, but balanced is outside the BEST score's tie set.
    metrics = {
        'baseline': dict(macro_f1=.75, accuracy=.90),
        'sqrt_balanced': dict(macro_f1=.7499992, accuracy=.91),
        'balanced': dict(macro_f1=.7499984, accuracy=.92),
    }
    assert select_candidate(metrics) == 'sqrt_balanced'


def evaluation_fixture(changed=False):
    frame = pd.DataFrame([
        dict(id='validation:1', sentiment='negative', topic='lecturer'),
        dict(id='validation:2', sentiment='neutral', topic='other'),
        dict(id='validation:3', sentiment='positive', topic='facility')])
    sentiments = ['negative', 'positive', 'positive'] if not changed else ['positive', 'neutral', 'positive']
    topics = ['lecturer', 'lecturer', 'facility'] if not changed else ['lecturer', 'curriculum', 'facility']
    cases = [dict(id='a', text='ambiguous', group='unknown', sentiment=None, topic=None),
             dict(id='b', text='clear', group='clear', sentiment='positive', topic='lecturer')]
    case_pred = [dict(sentiment='positive', topic='lecturer'),
                 dict(sentiment='negative' if changed else 'positive', topic='lecturer')]
    from ml.labels import SENTIMENT_LABELS, TOPIC_LABELS
    return frame, dict(split='validation',
        metrics={'sentiment': score_labels(frame.sentiment.tolist(), sentiments, list(SENTIMENT_LABELS)),
                 'topic': score_labels(frame.topic.tolist(), topics, list(TOPIC_LABELS))},
        prediction_rows=[dict(id=rid, sentiment=s, topic=t)
                         for rid, s, t in zip(frame.id, sentiments, topics)],
        known_cases=score_cases(cases, case_pred))


def test_comparison_exposes_per_class_losses_and_correct_to_wrong_ids():
    frame, base = evaluation_fixture()
    _, candidate = evaluation_fixture(True)
    result = compare_results(base, candidate, frame)
    assert result['metrics']['sentiment']['per_class'][0]['recall'] == -1
    assert result['metrics']['sentiment']['per_class'][1]['recall'] == 1
    assert result['validation']['sentiment']['regressed'] == ['validation:1']
    assert result['validation']['sentiment']['improved'] == ['validation:2']
    # Wrong-to-wrong topic change must still be visible.
    assert result['validation']['topic']['changed'][0] == {
        'id': 'validation:2', 'expected': 'other', 'before': 'lecturer', 'after': 'curriculum'}
    assert result['known_cases']['sentiment']['regressed'] == ['b']
    assert result['known_cases']['sentiment']['scored'] == 1
    assert result['known_cases']['topic']['scored'] == 1


@pytest.mark.parametrize('mutation', ['order', 'missing', 'case_truth'])
def test_comparison_rejects_changed_alignment_or_expectations(mutation):
    frame, base = evaluation_fixture()
    candidate = copy.deepcopy(base)
    if mutation == 'order':
        candidate['prediction_rows'].reverse()
    elif mutation == 'missing':
        candidate['prediction_rows'].pop()
    else:
        candidate['known_cases']['rows'][0]['sentiment'] = 'neutral'
    with pytest.raises(ValueError, match='align|expect'):
        compare_results(base, candidate, frame)


@pytest.mark.parametrize('destination', ['models', 'backend', 'root', 'existing_run'])
def test_run_refuses_live_or_existing_outputs_before_any_fit(tmp_path, destination):
    from reports.ct2_class_weights import run_experiment
    root = tmp_path / 'project'
    root.mkdir()
    output = root if destination == 'root' else root / destination
    if destination == 'existing_run':
        output = root / '.local-tools/ct2-class-weights/existing'
        output.mkdir(parents=True)
        (output / 'keep.txt').write_text('original')
    with pytest.raises((ValueError, FileExistsError), match='output|exist|research'):
        run_experiment(root, output)
    if destination == 'existing_run':
        assert (output / 'keep.txt').read_text() == 'original'


@pytest.fixture
def small_project(tmp_path):
    """Real serialized pipelines and CT1 freeze, with NO test split on disk."""
    import hashlib
    import json
    from datetime import datetime, timezone
    from importlib.metadata import version
    import platform
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline
    from sklearn.svm import LinearSVC
    from ml.preprocessing import normalize_text
    from ml.train_sentiment import TFIDF_PARAMS, CLF_PARAMS
    from reports.ct_evaluation import create_baseline, evaluate, LABELS, ROOT
    root = tmp_path / 'project'
    for path in ['models', 'data/raw/train', 'data/raw/dev', 'reports/data',
                 'reports/quality', 'docs/quality', 'reports/metrics/sentiment',
                 'reports/metrics/topic']:
        (root / path).mkdir(parents=True, exist_ok=True)
    texts = [f'{sentiment} {topic} course repeated' for sentiment in LABELS['sentiment']
             for topic in LABELS['topic']] * 2
    sentiments = [str(i) for i in range(3) for _ in range(4)] * 2
    topics = [str(i) for _ in range(3) for i in range(4)] * 2
    for split in ['train', 'dev']:
        for name, values in [('sents', texts), ('sentiments', sentiments), ('topics', topics)]:
            (root / f'data/raw/{split}/{name}.txt').write_text('\n'.join(values) + '\n', encoding='utf-8')
    for name in ['reports/data/source.json', 'reports/data/manifest.json']:
        (root / name).write_text('{}', encoding='utf-8')
    (root / 'docs/quality/ct1-protocol.md').write_text('Fixture protocol')
    (root / 'reports/ct_evaluation.py').write_bytes((ROOT / 'reports/ct_evaluation.py').read_bytes())
    cases = [dict(id='c1', text='positive lecturer', group='clear', sentiment='positive', topic='lecturer'),
             dict(id='c2', text='?', group='ambiguous', sentiment=None, topic=None)]
    (root / 'reports/quality/known-cases.json').write_text(json.dumps(dict(cases=cases)))
    from ml.data import load_split
    train = load_split(root / 'data/raw', 'train')
    pipes = {}
    for task in LABELS:
        pipes[task] = Pipeline([('tfidf', TfidfVectorizer(preprocessor=normalize_text, **TFIDF_PARAMS)),
                              ('clf', LinearSVC(**CLF_PARAMS['linear_svm']))])
        pipes[task].fit(train.text.tolist(), train[task].tolist())
    evaluation = evaluate(root, pipes, cases)
    for task, pipeline in pipes.items():
        artifact = root / f'models/{task}_pipeline.joblib'
        joblib.dump(pipeline, artifact)
        metadata = dict(contract_version='1.0', task=task, algorithm='linear_svm',
            artifact_filename=artifact.name, artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
            labels=LABELS[task], python_version=platform.python_version(),
            package_versions={p: version(p) for p in ['numpy', 'scipy', 'pandas', 'scikit-learn', 'joblib']},
            dataset_manifest_sha256=hashlib.sha256(b'{}').hexdigest(),
            preprocessing=dict(name='ml.preprocessing.normalize_text', version='1.0'),
            parameters=dict(tfidf={**TFIDF_PARAMS, 'preprocessor': 'ml.preprocessing.normalize_text'},
                classifier=dict(name='linear_svm', **CLF_PARAMS['linear_svm'])),
            selection=dict(algorithm='linear_svm', metric='macro_f1', validation_metrics=evaluation['metrics'][task]),
            trained_at=datetime.now(timezone.utc).isoformat())
        (root / f'models/{task}_metadata.json').write_text(json.dumps(metadata))
        comparison = dict(selection=dict(algorithm='linear_svm'),
                          validation=dict(linear_svm=evaluation['metrics'][task]),
                          test=dict(linear_svm={'status': 'fixture historical only'}))
        (root / f'reports/metrics/{task}/comparison.json').write_text(json.dumps(comparison))
    baseline = root / 'reports/evidence/ct1/baseline-v2'
    snapshot = root / '.local-tools/ct1-baseline-v2'
    create_baseline(root, baseline, snapshot)
    return root, baseline, snapshot


def test_experiment_real_fixture_lifecycle_has_no_test_split_and_preserves_baseline(small_project):
    from reports.ct2_class_weights import run_experiment, verify_experiment
    from reports.ct_evaluation import read, verify_inventory
    root, baseline, snapshot = small_project
    output = root / '.local-tools/ct2-class-weights/run'
    run_experiment(root, output, baseline, snapshot)
    result = read(output / 'results.json')
    assert result['selection'] == {'sentiment': 'baseline', 'topic': 'baseline'}
    assert result['promotion'] == 'not_deployed'
    assert len(result['candidates']) == 3
    assert verify_experiment(root, output, baseline, snapshot)['verified'] is True
    verify_inventory(root, read(baseline / 'inventory.json'))
    assert not (root / 'data/raw/test').exists()


@pytest.mark.parametrize('tamper', ['metrics', 'artifact', 'missing_receipt', 'live_source'])
def test_replay_rejects_changed_evidence_or_source(small_project, tamper):
    from reports.ct2_class_weights import run_experiment, verify_experiment
    root, baseline, snapshot = small_project
    output = root / '.local-tools/ct2-class-weights/run'
    run_experiment(root, output, baseline, snapshot)
    if tamper == 'missing_receipt':
        (output / 'receipt.json').unlink()
    else:
        path = {'metrics': output / 'results.json',
                'artifact': output / 'candidates/balanced/sentiment_pipeline.joblib',
                'live_source': root / 'data/raw/train/sents.txt'}[tamper]
        path.write_bytes(b'changed')
    with pytest.raises((ValueError, FileNotFoundError)):
        verify_experiment(root, output, baseline, snapshot)
