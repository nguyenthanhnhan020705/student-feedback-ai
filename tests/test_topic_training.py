"""Contract behavior on authored fixtures; not evidence of corpus accuracy."""
import pandas as pd
import pytest

from ml.evaluate_topic import evaluate_models, metrics_for_predictions
from ml.train_topic import train_models, select_model
from ml.predict_topic import predict_texts


def topic_frame(split='train'):
    samples = [('lecturer', 'giảng viên dạy tốt'),
               ('curriculum', 'chương trình môn học'),
               ('facility', 'phòng học máy chiếu'),
               ('other', 'hoạt động đoàn hội')]
    rows = [(f'{split}:{i:06d}', text, 'positive', label, split)
            for i, (label, text) in enumerate(samples * 3, 1)]
    return pd.DataFrame(rows, columns=['id', 'text', 'sentiment', 'topic', 'split'])


@pytest.fixture(scope='module')
def models():
    return train_models(topic_frame())


def test_four_class_predictions_preserve_input_order(models):
    texts = ['phòng học máy chiếu', 'giảng viên dạy tốt',
             'hoạt động đoàn hội', 'chương trình môn học']
    for model in models.values():
        assert predict_texts(model, texts) == ['facility', 'lecturer', 'other', 'curriculum']
        assert predict_texts(model, []) == []


@pytest.mark.parametrize('bad', ['text', [None], [' '], [123]])
def test_predict_rejects_invalid_input(models, bad):
    with pytest.raises(ValueError):
        predict_texts(models['nb'], bad)


@pytest.mark.parametrize('mutation', ['wrong_split', 'missing_class', 'unknown', 'null', 'blank', 'empty'])
def test_training_rejects_invalid_frame(mutation):
    frame = topic_frame()
    if mutation == 'wrong_split':
        frame.loc[0, 'split'] = 'test'
    elif mutation == 'missing_class':
        frame = frame[frame.topic != 'other']
    elif mutation == 'unknown':
        frame.loc[0, 'topic'] = 'invalid'
    elif mutation == 'null':
        frame.loc[0, 'topic'] = None
    elif mutation == 'blank':
        frame.loc[0, 'text'] = ' '
    else:
        frame = frame.iloc[:0]
    with pytest.raises(ValueError):
        train_models(frame)


def test_validation_and_evaluation_do_not_fit_or_extend_vocabulary(models):
    validation = topic_frame('validation')
    validation['text'] += ' validationonlytoken'
    snapshots = {k: dict(v.named_steps['tfidf'].vocabulary_) for k, v in models.items()}
    selection = select_model(models, validation)
    assert selection['metric'] == 'macro_f1'
    evaluate_models(models, topic_frame('test'))
    for key, model in models.items():
        assert model.named_steps['tfidf'].vocabulary_ == snapshots[key]
        assert 'validationonlytoken' not in snapshots[key]
    with pytest.raises(ValueError):
        select_model(models, topic_frame('test'))


def test_metrics_count_all_four_classes_in_canonical_order():
    metrics = metrics_for_predictions(
        ['lecturer', 'lecturer', 'curriculum', 'facility'],
        ['lecturer', 'curriculum', 'curriculum', 'other'])
    assert metrics['confusion_matrix'] == [[1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
    assert metrics['accuracy'] == .5
    assert metrics['macro_f1'] == pytest.approx(1 / 3)
    assert [row['support'] for row in metrics['per_class']] == [2, 1, 1, 0]


@pytest.mark.parametrize('scores,winner', [
    ([(.5, .6), (.5, .6), (.5, .6)], 'nb'),
    ([(.5, .6), (.5000005, .7), (.4, .9)], 'logistic_regression'),
    ([(.5, .9), (.6, .5), (.7, .4)], 'linear_svm'),
])
def test_selection_uses_macro_f1_then_accuracy_then_fixed_order(monkeypatch, scores, winner):
    # Controlled scores isolate tolerance/tie policy from classifier fitting.
    metrics = {name: {'macro_f1': f1, 'accuracy': acc}
               for name, (f1, acc) in zip(('nb', 'logistic_regression', 'linear_svm'), scores)}
    monkeypatch.setattr('ml.train_topic.evaluate_models', lambda *_: metrics)
    assert select_model({}, topic_frame('validation'))['algorithm'] == winner
