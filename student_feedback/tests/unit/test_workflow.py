import pytest

def test_training_refuses_serving_before_reading_data(tmp_path):
    from feedback_ai.training.workflow import train
    with pytest.raises(ValueError,match='serving'):
        train('sentiment',tmp_path/'missing',tmp_path/'artifacts/serving',tmp_path/'missing.json')

def test_training_refuses_existing_output(tmp_path):
    from feedback_ai.training.workflow import train
    with pytest.raises(FileExistsError):
        train('topic',tmp_path/'missing',tmp_path,tmp_path/'missing.json')

def test_experiment_algorithms_are_importable():
    from feedback_ai.training.experiments.class_weights import class_weights
    assert class_weights('sentiment',['negative','neutral','positive'],'minority_x2')['neutral']==2
    from feedback_ai.training.experiments.word_char import CHAR_WEIGHTS
    assert CHAR_WEIGHTS==(.5,1.,2.)
    from feedback_ai.training.experiments.augmentation import RATIOS
    assert RATIOS==(.25,.5,1.)
    from feedback_ai.training.experiments.selective import QUANTILES
    assert QUANTILES['zero_plus_margin_q10']==.1
