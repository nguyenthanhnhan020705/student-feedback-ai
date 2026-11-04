import unittest
import ml.labels as labels


class LabelTests(unittest.TestCase):
    def test_canonical_order_and_mapping(self):
        self.assertEqual(labels.SENTIMENT_LABELS, ('negative', 'neutral', 'positive'))
        self.assertEqual(labels.TOPIC_LABELS, ('lecturer', 'curriculum', 'facility', 'other'))
        self.assertEqual(labels.SENTIMENT_SOURCE_MAP, {'0': 'negative', '1': 'neutral', '2': 'positive'})
        self.assertEqual(labels.TOPIC_SOURCE_MAP, {'0': 'lecturer', '1': 'curriculum', '2': 'facility', '3': 'other'})
