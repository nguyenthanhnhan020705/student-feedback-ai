import unittest
from ml.preprocessing import normalize_text


class NormalizeTests(unittest.TestCase):
    def test_normalization_and_preservation(self):
        self.assertEqual(normalize_text('  KHÔNG\ttốt!!! 😢 123\n'), 'không tốt!!! 😢 123')

    def test_empty(self):
        self.assertEqual(normalize_text(' \n\t'), '')

    def test_non_string(self):
        with self.assertRaises(TypeError):
            normalize_text(None)

    def test_idempotent(self):
        text = normalize_text('  Câu  THỬ! ')
        self.assertEqual(normalize_text(text), text)
