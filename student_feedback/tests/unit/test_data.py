import tempfile
import unittest
from pathlib import Path
import feedback_ai.data.loader as data


class DataContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for split in ('train', 'dev', 'test'):
            folder = self.root / split
            folder.mkdir()
            for name, content in {'sents.txt': '  KHÔNG tốt!  \nCâu hai\n', 'sentiments.txt': '0\n2\n', 'topics.txt': '0\n3\n'}.items():
                (folder / name).write_text(content, encoding='utf-8-sig')

    def test_raw_text_schema_labels_and_ids(self):
        frame = data.load_split(self.root, 'validation')
        self.assertEqual(list(frame.columns), ['id', 'text', 'sentiment', 'topic', 'split'])
        self.assertEqual(frame.iloc[0].to_dict(), dict(id='validation:000001', text='  KHÔNG tốt!  ', sentiment='negative', topic='lecturer', split='validation'))
        self.assertEqual(frame.iloc[1]['topic'], 'other')

    def test_dataset_keys(self):
        self.assertEqual(list(data.load_dataset(self.root)), ['train', 'validation', 'test'])

    def test_reject_misaligned_lines(self):
        (self.root / 'train/topics.txt').write_text('0\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'train.*count'):
            data.load_split(self.root, 'train')

    def test_reject_unknown_code_with_id(self):
        (self.root / 'train/topics.txt').write_text('9\n3\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'train:000001.*topic'):
            data.load_split(self.root, 'train')

    def test_reject_blank_text(self):
        (self.root / 'train/sents.txt').write_text(' \nCâu hai\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'train:000001.*text'):
            data.load_split(self.root, 'train')

    def test_missing_file(self):
        (self.root / 'train/topics.txt').unlink()
        with self.assertRaises(FileNotFoundError):
            data.load_split(self.root, 'train')

    def test_invalid_split(self):
        with self.assertRaises(ValueError):
            data.load_split(self.root, 'dev')

    def test_empty_split_is_invalid(self):
        for path in (self.root / 'train').iterdir():
            path.write_text('', encoding='utf-8')
        with self.assertRaises(ValueError):
            data.load_split(self.root, 'train')

    def test_manifest_counts_duplicates_without_exposing_text(self):
        report = data.inspect_data(self.root)
        self.assertEqual(report['schema_version'], '1.0')
        self.assertEqual(report['splits']['train']['rows'], 2)
        self.assertEqual(report['duplicates']['across_splits'][0]['overlap_unique_texts'], 2)
        self.assertNotIn('KHÔNG', str(report))
        self.assertEqual(len(report['splits']['train']['files'][0]['sha256']), 64)

    def test_manifest_write(self):
        result = data.write_manifest(self.root / 'manifest.json', self.root)
        self.assertTrue((self.root / 'manifest.json').is_file())
        self.assertEqual(result['splits']['test']['label_counts']['topic']['other'], 1)

    def test_all_source_labels_are_available(self):
        folder = self.root / 'train'
        (folder / 'sents.txt').write_text('a\nb\nc\nd\n', encoding='utf-8')
        (folder / 'sentiments.txt').write_text('0\n1\n2\n0\n', encoding='utf-8')
        (folder / 'topics.txt').write_text('0\n1\n2\n3\n', encoding='utf-8')
        frame = data.load_split(str(self.root), 'train')
        self.assertEqual(frame.sentiment.tolist(), ['negative', 'neutral', 'positive', 'negative'])
        self.assertEqual(frame.topic.tolist(), ['lecturer', 'curriculum', 'facility', 'other'])

    def test_duplicate_comparison_does_not_mutate_raw_text(self):
        (self.root / 'train/sents.txt').write_text('  CÂU A\ncâu a\n', encoding='utf-8')
        report = data.inspect_data(self.root)
        self.assertEqual(report['duplicates']['within_split']['train'], 2)
        self.assertEqual(data.load_split(self.root, 'train').text.iloc[0], '  CÂU A')

    def test_blank_sentiment_is_rejected(self):
        (self.root / 'train/sentiments.txt').write_text('\n2\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'train:000001.*sentiment'):
            data.load_split(self.root, 'train')

    def test_canonical_validation_folder(self):
        (self.root / 'dev').rename(self.root / 'validation')
        self.assertEqual(data.load_split(self.root, 'validation').split.iloc[0], 'validation')

    def test_preserves_unicode_line_separator_inside_sentence(self):
        (self.root / 'train/sents.txt').write_text('a\u2028b\nsecond\n', encoding='utf-8')
        frame = data.load_split(self.root, 'train')
        self.assertEqual(frame.text.iloc[0], 'a\u2028b')

    def test_manifest_uses_explicit_source_evidence(self):
        source = {'url': 'https://example.org/fixture', 'revision': 'fixture-v1',
                  'permission_evidence': 'fixture', 'approval_status': 'pending_leader_review'}
        manifest = data.write_manifest(self.root / 'manifest.json', self.root, source=source)
        self.assertEqual(manifest['source'], source)

    def test_failed_validation_does_not_overwrite_existing_manifest(self):
        target = self.root / 'manifest.json'
        target.write_text('previous', encoding='utf-8')
        (self.root / 'train/topics.txt').unlink()
        with self.assertRaises(FileNotFoundError):
            data.write_manifest(target, self.root)
        self.assertEqual(target.read_text(encoding='utf-8'), 'previous')

@unittest.skipUnless(__import__('os').environ.get('TV2_RUN_REAL_DATA') == '1',
                     'Set TV2_RUN_REAL_DATA=1 after downloading the pinned source')
class RealDatasetTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[2]

    def read(self, name):
        import json
        return json.loads((self.ROOT / 'data' / name).read_text(encoding='utf-8'))

    def test_downloaded_bytes_match_recorded_source(self):
        source = self.read('source.json')
        self.assertEqual(len(source['files']), 9)
        for item in source['files']:
            path = item['path'].replace('dev/', 'validation/', 1)  # source calls the split `dev`; this project stores `validation`
            self.assertEqual(data.sha256_file(self.ROOT / 'data/raw' / path), item['sha256'])

    def test_complete_dataset_matches_manifest(self):
        manifest = self.read('manifest.json')
        for split, frame in data.load_dataset(self.ROOT / 'data/raw').items():
            self.assertEqual(len(frame), manifest['splits'][split]['rows'])
            self.assertEqual(list(frame.columns), data.COLUMNS)
            self.assertTrue(all(isinstance(value, str) for row in frame.itertuples(index=False, name=None) for value in row))

    def test_manifest_reproducible_from_real_source(self):
        self.assertEqual(data.inspect_data(self.ROOT / 'data/raw', source=self.read('source.json')), self.read('manifest.json'))
        self.assertTrue(self.read('manifest.json')['source']['revision'], 'validate must record the pinned source revision')
