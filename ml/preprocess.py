"""TV2: extend only after checking the dataset and preserving its splits."""

import unicodedata


def normalize_text(text: str) -> str:
    """Normalize Unicode and whitespace, preserving accents, case and punctuation.

    If used in training, include this function in the saved vectorizer/pipeline
    so inference applies exactly the same transformation. No vocabulary is fit
    here. TV2 owns conversion of the source corpus to the three CSV splits.
    """
    if not isinstance(text, str):
        raise TypeError('text must be a string')
    return ' '.join(unicodedata.normalize('NFC', text).split())
