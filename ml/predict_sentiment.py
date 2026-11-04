"""Dự đoán nhãn cảm xúc từ pipeline đã fit."""
from __future__ import annotations

from typing import Any


def predict_texts(pipeline: Any, texts: list[str]) -> list[str]:
    if not isinstance(texts, list):
        raise ValueError("texts phải là list")
    if texts == []:
        return []
    for i, text in enumerate(texts):
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Phần tử {i} phải là chuỗi không rỗng")
    return [str(label) for label in pipeline.predict(texts)]