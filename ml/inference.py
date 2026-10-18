"""Use predictions from a trusted, already trained text pipeline only."""

from numbers import Integral

from ml.labels import LABELS


def predict_codes(pipeline, texts: list[str], task: str) -> list[int]:
    """Reject mismatched output lengths and unknown/non-integer labels."""
    predictions = list(pipeline.predict(texts))
    if len(predictions) != len(texts):
        raise ValueError('Model returned the wrong number of predictions')
    codes = []
    for code in predictions:
        if isinstance(code, bool) or not isinstance(code, Integral) or code not in LABELS[task]:
            raise ValueError(f'Invalid {task} label from model')
        codes.append(int(code))
    return codes
