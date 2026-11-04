"""CT5: reject denominator inflation, invalid scores and in-sample thresholds."""
import copy
import hashlib

import numpy as np
import pandas as pd
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from ml.labels import SENTIMENT_LABELS, TOPIC_LABELS
from reports.ct5_selective_prediction import (
    extract_signals, partition_validation, fit_thresholds, apply_policy, summarize,
)


def fitted(combined=False, task='sentiment'):
    labels = SENTIMENT_LABELS if task == 'sentiment' else TOPIC_LABELS
    texts = [f'{label} tiếng Việt giảng bài' for label in labels] * 3
    word = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b')
    features = FeatureUnion([
        ('word', word), ('char', TfidfVectorizer(analyzer='char', ngram_range=(2, 3))),
    ]) if combined else word
    return Pipeline([('features', features), ('clf', LinearSVC(random_state=42))]).fit(texts, list(labels)*3)


@pytest.mark.parametrize('combined', [False, True])
def test_real_features_scores_class_order_and_zero_vector(combined):
    pipe = fitted(combined)
    # Reorder coefficients/classes together: a consumer must use actual class columns.
    clf = pipe.steps[-1][1]
    order = [2, 0, 1]
    clf.classes_ = clf.classes_[order]
    clf.coef_ = clf.coef_[order]
    clf.intercept_ = clf.intercept_[order]
    texts = ['positive tiếng', 'giảngx', '🦄🦄']
    actual = extract_signals(pipe, texts, 'sentiment')
    scores = pipe.decision_function(texts)
    assert [r['prediction'] for r in actual] == list(pipe.predict(texts))
    for i, row in enumerate(actual):
        assert row['classes'] == list(clf.classes_)
        assert row['scores'] == list(scores[i])
        assert row['gap'] == pytest.approx(sorted(scores[i])[-1] - sorted(scores[i])[-2])
    assert actual[2]['nnz'] == 0
    if combined:
        assert actual[1]['branch_nnz']['word'] == 0
        assert actual[1]['branch_nnz']['char'] > 0
        assert actual[1]['nnz'] > 0
    else:
        assert actual[1]['nnz'] == 0


@pytest.mark.parametrize('bad', ['nan', 'shape', 'classes', 'prediction', 'exception'])
def test_model_failures_are_errors_not_abstentions(monkeypatch, bad):
    pipe = fitted()
    clf = pipe.steps[-1][1]
    if bad == 'classes':
        clf.classes_ = np.array(['negative', 'neutral', 'alien'])
    elif bad == 'prediction':
        monkeypatch.setattr(pipe, 'predict', lambda text: np.array(['negative']))
    elif bad == 'exception':
        def broken(text):
            raise RuntimeError('model failure')
        monkeypatch.setattr(clf, 'decision_function', broken)
    else:
        monkeypatch.setattr(clf, 'decision_function', lambda features: np.array([[np.nan, 0., 1.]]) if bad == 'nan' else np.array([1.]))
    with pytest.raises((ValueError, RuntimeError)):
        extract_signals(pipe, ['positive'], 'sentiment')


def signal(label, nnz=1, gap=1.):
    return dict(prediction=label, nnz=nnz, gap=gap, branch_nnz={'word': nnz})


def rows_and_signals():
    rows = [dict(id=str(i), text='text', source_group=str(i),
                 sentiment='positive', topic='lecturer') for i in range(4)]
    signals = dict(sentiment=[signal('positive'), signal('negative'), signal('positive', 0), signal('negative', 0)],
                   topic=[signal('lecturer') for _ in rows])
    return rows, signals


def test_quantiles_use_only_nonzero_development_per_task_and_linear_method():
    _, signals = rows_and_signals()
    signals['sentiment'] = [signal('positive', 1, 0.), signal('positive', 1, 10.),
                            signal('positive', 0, 100.), signal('positive', 1, 999.)]
    signals['topic'] = [signal('lecturer', 1, 100.), signal('lecturer', 1, 200.),
                        signal('lecturer', 1, 300.), signal('lecturer', 1, 9999.)]
    thresholds = fit_thresholds(signals, [0, 1, 2])
    assert thresholds['zero_plus_margin_q10'] == {'sentiment': 1., 'topic': 120.}
    assert thresholds['zero_plus_margin_q05']['sentiment'] == .5
    assert thresholds['zero_plus_margin_q20']['sentiment'] == 2.
    assert fit_thresholds(signals, [])['zero_plus_margin_q10']['sentiment'] is None
    signals['sentiment'] = [signal('positive', 0) for _ in range(4)]
    assert fit_thresholds(signals, [0, 1])['zero_plus_margin_q10']['sentiment'] is None


def test_hash_group_partition_does_not_split_accents_case_whitespace_variants():
    texts = ['ĐẸP quá', 'dep qua', ' Đẹp   quá ', 'Bình thường', 'Tệ lắm']
    frame = pd.DataFrame([dict(id=str(i), text=t, sentiment='positive', topic='lecturer') for i, t in enumerate(texts)])
    result = partition_validation(frame)
    assert len(result['rows']) == 5
    first = result['rows'][:3]
    assert len({r['source_group'] for r in first}) == 1
    assert len({r['subset'] for r in first}) == 1
    for row in result['rows']:
        expected = hashlib.sha256(('ct5-v1|42|' + row['group_key']).encode()).hexdigest()
        assert row['group_digest'] == expected
        assert row['subset'] == ('threshold_development' if int(expected[:2], 16) < 128 else 'policy_audit')
    empty = partition_validation(frame.iloc[:0])
    assert empty['status'] == 'insufficient_partition'
    assert partition_validation(frame.iloc[:1])['status'] == 'insufficient_partition'


def test_policy_zero_complete_features_boundary_gap_and_all_or_nothing():
    rows, signals = rows_and_signals()
    signals['sentiment'][0]['branch_nnz'] = {'word': 0, 'char': 1}
    signals['sentiment'][1]['gap'] = .499
    thresholds = {'zero_plus_margin_q10': {'sentiment': .5, 'topic': 1.}}
    result = apply_policy(rows, signals, 'zero_plus_margin_q10', thresholds)
    assert result[0]['accepted_pair'] and result[0]['labels_for_display'] == {'sentiment':'positive', 'topic':'lecturer'}
    assert not result[1]['accepted_pair'] and result[1]['accepted']['topic']
    assert result[1]['labels_for_display'] is None
    assert result[1]['reasons'] == ['low_margin_sentiment']
    assert 'zero_features_sentiment' in result[2]['reasons']
    assert result[1]['raw_prediction']['sentiment'] == 'negative'
    assert all(r['accepted_pair'] for r in apply_policy(rows, signals, 'always_answer', {}))
    thresholds['zero_plus_margin_q10']['sentiment'] = None
    with pytest.raises(ValueError, match='threshold'):
        apply_policy(rows, signals, 'zero_plus_margin_q10', thresholds)


def test_hand_derived_coverage_risk_and_rejected_correct_are_separate():
    rows, signals = rows_and_signals()
    result = summarize(apply_policy(rows, signals, 'zero_features', {}))
    assert result['input_count'] == 4 and result['accepted_pair_count'] == 2
    assert result['pair_coverage'] == .5 and result['abstention_rate'] == .5
    joint = result['joint']
    assert joint['correct_answered'] == joint['wrong_answered'] == 1
    assert joint['rejected_correct'] == joint['rejected_wrong'] == 1
    assert joint['accepted_accuracy'] == joint['selective_risk'] == .5
    assert joint['correct_and_answered_rate'] == joint['answered_wrong_rate'] == .25
    assert joint['rejected_correct_rate'] == .25
    assert sum(joint[k] for k in ['correct_answered','wrong_answered','rejected_correct','rejected_wrong']) == joint['n_labeled']
    topic = result['tasks']['topic']
    assert topic['coverage'] == 1.
    assert topic['accepted_metrics']['n_rows'] == 4
    assert topic['pair_accepted_metrics']['n_rows'] == 2
    assert topic['accepted_metrics']['label_order'] == list(TOPIC_LABELS)
    assert topic['accepted_metrics']['per_class'][1]['support'] == 0
    baseline = summarize(apply_policy(rows, signals, 'always_answer', {}))
    assert joint['correct_and_answered_rate'] <= baseline['joint']['correct_and_answered_rate']


def test_null_truth_never_becomes_neutral_other_or_answerability():
    rows, signals = rows_and_signals()
    rows[0].update(sentiment=None, topic=None, group='ood')
    rows[1].update(sentiment=None, group='ambiguous')
    original = copy.deepcopy(rows)
    decisions = apply_policy(rows, signals, 'zero_features', {})
    result = summarize(decisions)
    assert rows == original
    assert result['input_count'] == 4 and result['joint']['n_labeled'] == 2
    assert result['joint']['accepted_labeled'] == 0
    assert result['joint']['accepted_accuracy'] is None
    assert result['joint']['correct_and_answered_rate'] == 0.
    assert result['answerability']['status'] == 'no_reviewed_answerability'
    assert result['answerability']['pair']['false_reject_rate'] is None
    assert result['tasks']['sentiment']['accepted_metrics'] is None
    assert summarize([])['pair_coverage'] is None


def test_answerability_denominators_and_ambiguous_are_explicit():
    rows, signals = rows_and_signals()
    for row, value in zip(rows, ['answerable','unanswerable','answerable','ambiguous']):
        row['answerability'] = {'sentiment': value, 'topic': value}
    result = summarize(apply_policy(rows, signals, 'zero_features', {}))['answerability']
    for unit in ['sentiment', 'pair']:
        r = result[unit]
        assert r['answerable'] == 2 and r['unanswerable'] == 1 and r['ambiguous'] == 1
        assert r['false_reject_rate'] == .5
        assert r['unsafe_accept_rate'] == 1.
        assert r['precision_of_abstention'] == 0.
        assert r['accepted_answerable_metrics']['n_rows'] == 1


from test_ct4_augmentation import lifecycle as ct4_fixture


@pytest.fixture(scope='module')
def ct5_project(ct4_fixture):
    from reports.ct4_augmentation import run_experiment as run4
    root, ct3 = ct4_fixture
    ct4 = root / '.local-tools/ct4-augmentation/run-1'
    run4(root, ct4, ct3)
    return root, ct4


@pytest.fixture(scope='module')
def completed_run(ct5_project):
    from reports.ct5_selective_prediction import run_experiment
    from unittest.mock import patch
    root, ct4 = ct5_project
    output = root / '.local-tools/ct5-selective-prediction/run-1'
    def forbidden(*args, **kwargs):
        raise AssertionError('CT5 must not fit')
    with patch.object(Pipeline, 'fit', forbidden), patch.object(LinearSVC, 'fit', forbidden):
        result = run_experiment(root, output, ct4)
    assert result['status'] == 'engineering_complete_independent_evaluation_pending'
    return root, ct4, output


def test_serialized_lifecycle_without_test_split_and_fresh_no_fit_replay(completed_run):
    import json
    import subprocess
    import sys
    from reports.ct_evaluation import read
    root, ct4, output = completed_run
    assert not (root / 'data/raw/test').exists()
    config = read(output/'config.json')
    assert config['policies'] == ['always_answer', 'zero_features', 'zero_plus_margin_q05', 'zero_plus_margin_q10', 'zero_plus_margin_q20']
    assert config['recommended_policy'] is None
    results = read(output/'metrics.json')
    for pair in ['original', 'ct4']:
        for dataset in ['threshold_development', 'policy_audit', 'known', 'stress_unaccented_validation']:
            assert set(results[pair][dataset]) == set(config['policies'])
    decisions = read(output/'decisions.json')
    for pair in decisions.values():
        for dataset in pair.values():
            baseline = dataset['always_answer']
            for policy_rows in dataset.values():
                assert [(r['id'], r['raw_prediction']) for r in policy_rows] == [(r['id'], r['raw_prediction']) for r in baseline]
    code = '''
import sys
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
def forbidden(*a, **k): raise AssertionError('Fresh replay tried fitting')
Pipeline.fit = LinearSVC.fit = forbidden
from reports.ct5_selective_prediction import verify_experiment
import json
print(json.dumps(verify_experiment(*sys.argv[1:])))
'''
    process = subprocess.run([sys.executable, '-B', '-c', code, str(root), str(output), str(ct4)],
                             capture_output=True, text=True, check=True)
    assert json.loads(process.stdout)['verified']


@pytest.mark.parametrize('kind', ['live','research_root','existing','control','redirect'])
def test_paths_rejected_before_any_control_loading(tmp_path, kind):
    from reports.ct5_selective_prediction import run_experiment
    root = tmp_path/'project'
    root.mkdir()
    output = root/'.local-tools/ct5-selective-prediction/run'
    if kind == 'live': output = root/'models'
    elif kind == 'research_root': output = output.parent
    elif kind == 'control': output = root/'.local-tools/ct4-augmentation/run-1'
    elif kind == 'existing': output.mkdir(parents=True)
    else:
        import subprocess
        external = tmp_path/'external'
        external.mkdir()
        output.parent.parent.mkdir(parents=True)
        try:
            output.parent.symlink_to(external, target_is_directory=True)
        except OSError:
            subprocess.run(['cmd','/c','mklink','/J',str(output.parent),str(external)],check=True,capture_output=True)
    with pytest.raises((ValueError, FileExistsError), match='output|path|research|exist'):
        run_experiment(root, output)


@pytest.mark.parametrize('tamper', ['model','source','parent','config','partition','thresholds','labels',
    'metrics','extra','nested_receipt','missing_receipt','schema','promotion','runtime','code',
    'rehash_thresholds','rehash_metrics','rehash_partition','rehash_labels','rehash_config','rehash_status','escape',
    'deployment','recommendation','status','missing_field'])
def test_replay_rejects_tampering_including_rehashed_semantics(completed_run, tmp_path, tamper):
    import json
    import shutil
    from reports.ct5_selective_prediction import verify_experiment
    from reports.ct_evaluation import read, digest
    root, _, _ = completed_run
    copied = tmp_path/'project'
    shutil.copytree(root, copied)
    ct4 = copied/'.local-tools/ct4-augmentation/run-1'
    output = copied/'.local-tools/ct5-selective-prediction/run-1'
    receipt = read(output/'receipt.json')
    if tamper == 'missing_receipt':
        (output/'receipt.json').unlink()
    elif tamper in ('schema','promotion','runtime','code','escape','deployment','recommendation','status','missing_field'):
        if tamper == 'schema': receipt['schema_version'] = 'ct5.bad'
        elif tamper == 'promotion': receipt['promotion'] = 'deployed'
        elif tamper == 'runtime': receipt['runtime']['python'] = '0.0'
        elif tamper == 'code': receipt['source_hashes']['reports/ct5_selective_prediction.py'] = '0'*64
        elif tamper == 'deployment': receipt['deployment'] = 'serving'
        elif tamper == 'recommendation': receipt['recommended_policy'] = 'always_answer'
        elif tamper == 'status': receipt['status'] = 'independently_certified'
        elif tamper == 'missing_field': del receipt['recommended_policy']
        else: receipt['payload']['../escape'] = '0'*64
        (output/'receipt.json').write_text(json.dumps(receipt),encoding='utf-8')
    elif tamper in ('extra', 'nested_receipt'):
        path = output/('extra.txt' if tamper == 'extra' else 'extra/receipt.json')
        path.parent.mkdir(exist_ok=True)
        path.write_text('{}',encoding='utf-8')
    elif tamper.startswith('rehash_'):
        name = {'thresholds':'thresholds.json','metrics':'metrics.json','partition':'partition.json',
                'labels':'decisions.json','config':'config.json','status':'data-status.json'}[tamper[7:]]
        value = read(output/name)
        if name == 'thresholds.json': value['original']['zero_plus_margin_q10']['sentiment'] += .1
        elif name == 'metrics.json': value['original']['policy_audit']['always_answer']['pair_coverage'] = .123
        elif name == 'partition.json': value['rows'][0]['subset'] = 'invented'
        elif name == 'decisions.json': value['original']['policy_audit']['always_answer'][0]['raw_prediction']['sentiment'] = 'alien'
        elif name == 'config.json': value['recommended_policy'] = 'zero_features'
        else: value['status'] = 'independently_certified'
        (output/name).write_text(json.dumps(value),encoding='utf-8')
        receipt['payload'][name] = digest(output/name)
        if name == 'config.json': receipt['config_sha256'] = digest(output/name)
        (output/'receipt.json').write_text(json.dumps(receipt),encoding='utf-8')
    else:
        path = {'model':copied/'models/sentiment_pipeline.joblib',
                'source':copied/'data/raw/dev/sents.txt','parent':ct4/'receipt.json',
                'config':output/'config.json','partition':output/'partition.json',
                'thresholds':output/'thresholds.json','labels':output/'decisions.json',
                'metrics':output/'metrics.json'}[tamper]
        path.write_bytes(b'changed')
    with pytest.raises((ValueError, FileNotFoundError)):
        verify_experiment(copied, output, ct4)
