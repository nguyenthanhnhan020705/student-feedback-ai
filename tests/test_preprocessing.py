
import pytest

from ml.preprocessing import normalize_text


def test_unicode_nfc():
    # "ế" ở dạng ký tự dựng sẵn và dạng tổ hợp phải tương đương.
    assert normalize_text("e\u0302\u0301") == "ế"


def test_collapse_whitespace():
    assert normalize_text("  thầy \t dạy\n tốt  ") == "thầy dạy tốt"


def test_empty_string():
    assert normalize_text("   ") == ""


def test_preserve_negation():
    text = "giảng viên không nhiệt tình"
    assert normalize_text(text) == text


def test_preserve_punctuation_and_emoji():
    text = "Không tốt!!! 😢"
    assert normalize_text(text) == text


def test_reject_non_string():
    with pytest.raises(TypeError):
        normalize_text(None)
