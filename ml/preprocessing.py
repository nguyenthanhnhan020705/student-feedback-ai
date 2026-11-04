"""Shared preprocessing for TF-IDF training and inference (contract v1.0)."""
import unicodedata


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError('text must be str')
    return ' '.join(unicodedata.normalize('NFC', text).lower().split())
