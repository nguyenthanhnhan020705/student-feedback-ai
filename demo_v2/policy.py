"""Independent per-task decisions; uncertainty never becomes neutral/other."""
import math
from ml.labels import SENTIMENT_LABELS, TOPIC_LABELS

LABELS = {'sentiment': SENTIMENT_LABELS, 'topic': TOPIC_LABELS}
MESSAGES = {
    'sentiment': 'Chưa đủ căn cứ để kết luận cảm xúc. Bạn có thể diễn đạt rõ nhận xét hơn.',
    'topic': 'Chưa đủ căn cứ để kết luận chủ đề. Bạn có thể nêu rõ đối tượng được nhận xét.',
}


def finite_nonnegative(value):
    if type(value) not in (int,float):
        return False
    try:
        return math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def decide_task(task, signal, threshold):
    if (task not in LABELS or not finite_nonnegative(threshold)
            or signal.get('prediction') not in LABELS[task]
            or type(signal.get('nnz')) is not int or signal['nnz'] < 0
            or not finite_nonnegative(signal.get('gap'))):
        raise ValueError('Invalid task signal/threshold')
    reason = 'zero_features' if signal['nnz'] == 0 else 'low_margin' if signal['gap'] < threshold else None
    if reason:
        return dict(status='insufficient_information', label=None, reason=reason, message=MESSAGES[task])
    return dict(status='answered', label=signal['prediction'], reason=None, message=None)


def make_prediction(signals, thresholds):
    parts = {task: decide_task(task, signals[task], thresholds[task]) for task in LABELS}
    count = sum(value['status'] == 'answered' for value in parts.values())
    return dict(contract_version='2.0', status={0:'insufficient',1:'partial',2:'complete'}[count], **parts)
