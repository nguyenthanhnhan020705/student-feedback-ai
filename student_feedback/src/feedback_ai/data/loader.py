"""Strict adapter for UIT-VSFC parallel text files; no fitting or row removal."""
import argparse
import hashlib
import json
from pathlib import Path
from typing import Literal

import pandas as pd

from feedback_ai.common.labels import SENTIMENT_SOURCE_MAP, TOPIC_SOURCE_MAP
from feedback_ai.data.preprocessing import normalize_text

SPLITS = ('train', 'validation', 'test')
COLUMNS = ['id', 'text', 'sentiment', 'topic', 'split']
SOURCE_FILES = ('sents.txt', 'sentiments.txt', 'topics.txt')


def _paths(data_dir: str | Path, split: str) -> list[Path]:
    if split not in SPLITS:
        raise ValueError(f'Invalid split: {split!r}; expected {SPLITS}')
    folder = Path(data_dir) / split
    if split == 'validation' and not folder.exists():
        folder = Path(data_dir) / 'dev'
    return [folder / name for name in SOURCE_FILES]


def load_split(data_dir: str | Path, split: Literal['train', 'validation', 'test']) -> pd.DataFrame:
    """Return raw strings and canonical labels; reject incomplete/invalid splits."""
    paths = _paths(data_dir, split)
    lines = []
    for path in paths:
        # Iterate physical lines only; str.splitlines() also splits U+2028 in text.
        with path.open(encoding='utf-8-sig', newline=None) as stream:
            lines.append([line.removesuffix('\n') for line in stream])
    counts = [len(items) for items in lines]
    if not counts[0] or len(set(counts)) != 1:
        raise ValueError(f'{split}: line count mismatch or empty split: {dict(zip(SOURCE_FILES, counts))}')
    rows = []
    for index, (text, sentiment, topic) in enumerate(zip(*lines), 1):
        record_id = f'{split}:{index:06d}'
        if not text.strip():
            raise ValueError(f'{record_id}: blank text in {paths[0].name}')
        labels = []
        for task, value, mapping in (
            ('sentiment', sentiment, SENTIMENT_SOURCE_MAP),
            ('topic', topic, TOPIC_SOURCE_MAP),
        ):
            if value not in mapping:
                raise ValueError(f'{record_id}: invalid {task} source code {value!r}')
            labels.append(mapping[value])
        rows.append((record_id, text, *labels, split))
    return pd.DataFrame(rows, columns=COLUMNS)


def load_dataset(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    return {split: load_split(data_dir, split) for split in SPLITS}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_data(data_dir: str | Path, *, source: dict | None = None) -> dict:
    """Inspect valid complete data; normalized overlap counts contain no sentences.

    Invalid records fail fast with location, rather than producing a partial manifest.
    Source revision and permission evidence must be supplied/reviewed separately.
    """
    root = Path(data_dir)
    report = {
        'schema_version': '1.0',
        'source': dict(source) if source is not None else {
            'revision': None, 'url': None, 'permission_evidence': None,
            'approval_status': 'pending_leader_review'},
        'splits': {},
        'duplicates': {'within_split': {}, 'across_splits': []},
        'policy': {'split_membership': 'preserve', 'duplicates': 'report_only',
                   'invalid_records': 'fail_fast',
                   'duplicate_comparison': 'feedback_ai.data.preprocessing.normalize_text v1.0'},
    }
    texts = {}
    for split, frame in load_dataset(root).items():
        normalized = frame.text.map(normalize_text)
        texts[split] = set(normalized)
        duplicates = int(normalized.duplicated(keep=False).sum())
        report['splits'][split] = {
            'rows': len(frame),
            'label_counts': {task: {key: int(value) for key, value in frame[task].value_counts().items()}
                             for task in ('sentiment', 'topic')},
            'empty_text_rows': 0, 'unknown_label_rows': 0,
            'unique_texts': len(texts[split]), 'duplicate_rows': duplicates,
            'files': [{'path': path.relative_to(root).as_posix(), 'sha256': sha256_file(path),
                       'file_bytes': path.stat().st_size} for path in _paths(root, split)],
        }
        report['duplicates']['within_split'][split] = duplicates
    for index, left in enumerate(SPLITS):
        for right in SPLITS[index + 1:]:
            report['duplicates']['across_splits'].append({
                'split_a': left, 'split_b': right,
                'overlap_unique_texts': len(texts[left] & texts[right]),
            })
    return report


def write_manifest(output_path: Path = Path('reports/data/manifest.json'),
                   data_dir: str | Path = Path('data/raw'), *, source: dict | None = None) -> dict:
    report = inspect_data(data_dir, source=source)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path('data/raw'))
    parser.add_argument('--output', type=Path, default=Path('reports/data/manifest.json'))
    parser.add_argument('--source-metadata', type=Path,
                        help='JSON with source URL/revision and permission evidence')
    args = parser.parse_args()
    source = json.loads(args.source_metadata.read_text(encoding='utf-8-sig')) if args.source_metadata else None
    write_manifest(args.output, args.data_dir, source=source)
