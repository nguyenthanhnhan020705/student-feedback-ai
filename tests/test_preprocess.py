import unicodedata

import pytest


def test_normalizes_unicode_and_whitespace_without_removing_accents():
    from ml.preprocess import normalize_text

    text = unicodedata.normalize('NFD', '  Giảng viên\t nhiệt tình.\n')
    assert normalize_text(text) == 'Giảng viên nhiệt tình.'
    assert normalize_text(normalize_text(text)) == normalize_text(text)


def test_empty_normalization_is_not_a_prediction():
    from ml.preprocess import normalize_text

    assert normalize_text(' \t\n') == ''
    with pytest.raises(TypeError):
        normalize_text(None)
