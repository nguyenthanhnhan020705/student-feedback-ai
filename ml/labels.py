"""Canonical labels and the source-code mapping specified by Data contract v1.0."""
SENTIMENT_LABELS = ('negative', 'neutral', 'positive')
TOPIC_LABELS = ('lecturer', 'curriculum', 'facility', 'other')
SENTIMENT_SOURCE_MAP = dict(zip(('0', '1', '2'), SENTIMENT_LABELS))
TOPIC_SOURCE_MAP = dict(zip(('0', '1', '2', '3'), TOPIC_LABELS))
