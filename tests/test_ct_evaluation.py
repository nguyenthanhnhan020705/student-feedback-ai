"""Safeguards for quality measurements, not assertions that models are perfect."""
import json
from pathlib import Path

import pytest

from reports.ct_evaluation import (
    score_labels, score_cases, verify_inventory, write_new_json, evaluate,
)


def test_metrics_include_unpredicted_minority_and_canonical_order():
    result = score_labels(['negative', 'neutral', 'positive'],
                          ['negative', 'negative', 'positive'],
                          ['negative', 'neutral', 'positive'])
    assert result['n_rows'] == 3
    assert result['accuracy'] == pytest.approx(2 / 3)
    assert result['per_class'][1] == dict(label='neutral', precision=0, recall=0, f1=0, support=1)
    assert result['label_order'] == ['negative', 'neutral', 'positive']
    assert result['confusion_matrix'] == [[1, 0, 0], [1, 0, 0], [0, 0, 1]]


@pytest.mark.parametrize('truth,pred', [([], []), (['negative'], []),
    (['negative'], ['invented']), (['unknown'], ['negative']), (['negative'], [None])])
def test_metric_input_corruption_is_not_silently_scored(truth, pred):
    with pytest.raises(ValueError):
        score_labels(truth, pred, ['negative', 'neutral', 'positive'])


def test_ambiguous_tasks_excluded_from_denominator_and_joint_score():
    cases = [dict(id='a', text='Tốt.', group='short', sentiment='positive', topic=None),
             dict(id='b', text='???', group='unknown', sentiment=None, topic=None),
             dict(id='c', text='Giảng viên tốt.', group='clear', sentiment='positive', topic='lecturer')]
    predictions = [dict(sentiment='positive', topic='lecturer') for _ in cases]
    result = score_cases(cases, predictions)
    assert result['sentiment']['scored'] == 2
    assert result['topic']['scored'] == 1
    assert result['joint']['scored'] == 1
    assert result['groups']['unknown']['sentiment']['accuracy'] is None
    assert result['rows'][1]['sentiment_correct'] is None


def test_case_alignment_and_unknown_prediction_fail():
    case = dict(id='a', text='Tốt', group='short', sentiment='positive', topic=None)
    with pytest.raises(ValueError):
        score_cases([case], [])
    with pytest.raises(ValueError):
        score_cases([case], [dict(sentiment='positive', topic='invented')])
    with pytest.raises(ValueError):
        score_cases([case, case], [dict(sentiment='positive', topic='lecturer')] * 2)


def test_inventory_detects_missing_or_tampered_protected_input(tmp_path):
    import hashlib
    p = tmp_path / 'artifact'
    p.write_bytes(b'baseline')
    inventory = {'artifact': hashlib.sha256(b'baseline').hexdigest()}
    verify_inventory(tmp_path, inventory)
    p.write_bytes(b'changed')
    with pytest.raises(ValueError, match='artifact'):
        verify_inventory(tmp_path, inventory)
    p.unlink()
    with pytest.raises(ValueError, match='artifact'):
        verify_inventory(tmp_path, inventory)


def test_evidence_is_never_overwritten(tmp_path):
    path = tmp_path / 'evidence.json'
    write_new_json(path, {'original': True})
    with pytest.raises(FileExistsError):
        write_new_json(path, {'original': False})
    assert json.loads(path.read_text()) == {'original': True}


def test_evaluator_accepts_validation_only(tmp_path):
    with pytest.raises(ValueError, match='validation'):
        evaluate(tmp_path, {}, [], split='test')


@pytest.mark.parametrize('extra', [True, False])
def test_evaluator_rejects_extra_or_missing_case_predictions(tmp_path, monkeypatch, extra):
    import pandas as pd
    from ml import data
    frame = pd.DataFrame([dict(id='validation:000001', text='validation text',
                               sentiment='positive', topic='lecturer', split='validation')])
    monkeypatch.setattr(data, 'load_split', lambda *a: frame)

    class Pipeline:
        def __init__(self, label):
            self.label = label

        def predict(self, texts):
            if texts == ['validation text']:
                return [self.label]
            return [self.label, 'invented'] if extra else []

    cases = [dict(id='known-1', text='case text', group='clear',
                  sentiment='positive', topic='lecturer')]
    with pytest.raises(ValueError, match='case prediction'):
        evaluate(tmp_path, dict(sentiment=Pipeline('positive'), topic=Pipeline('lecturer')), cases)

