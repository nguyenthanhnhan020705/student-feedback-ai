
import pandas as pd
import pytest

from ml.data import load_split


def write_csv(tmp_path, content):
    path = tmp_path / "UIT-VSFC_train.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_valid_csv(tmp_path):
    write_csv(
        tmp_path,
        'text,label\n"thầy dạy tốt",positive\n'
        '"không hiểu bài",negative\n',
    )
    df = load_split("train", tmp_path)

    assert len(df) == 2
    assert list(df.columns) == ["text", "label"]
    assert df.iloc[1]["text"] == "không hiểu bài"


def test_reject_empty_text(tmp_path):
    write_csv(tmp_path, "text,label\n   ,positive\n")
    with pytest.raises(ValueError, match="text rỗng"):
        load_split("train", tmp_path)


def test_reject_empty_label(tmp_path):
    write_csv(tmp_path, 'text,label\n"câu nhận xét",\n')
    with pytest.raises(ValueError, match="label rỗng"):
        load_split("train", tmp_path)


def test_reject_unknown_label(tmp_path):
    write_csv(tmp_path, 'text,label\n"câu nhận xét",mixed\n')
    with pytest.raises(ValueError, match="nhãn không hợp lệ"):
        load_split("train", tmp_path)


def test_reject_missing_column(tmp_path):
    write_csv(tmp_path, "sentence,label\ncâu nhận xét,positive\n")
    with pytest.raises(ValueError, match="cần đúng hai cột"):
        load_split("train", tmp_path)


def test_reject_unknown_split(tmp_path):
    with pytest.raises(ValueError, match="Split không hợp lệ"):
        load_split("development", tmp_path)
