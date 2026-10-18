"""Shared CLI wiring, without training or writing synthetic artifacts."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def training_cli(task: str) -> None:
    parser = argparse.ArgumentParser(description=f'Khung huan luyen {task}; chua trien khai.')
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data' / 'processed')
    parser.add_argument('--output', type=Path, default=ROOT / 'models' / f'{task}_pipeline.joblib')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    from ml.train_sentiment import train as train_sentiment
    from ml.train_topic import train as train_topic

    try:
        {'sentiment': train_sentiment, 'topic': train_topic}[task](
            args.data_dir, args.output, args.seed
        )
    except NotImplementedError as exc:
        parser.exit(2, f'{exc}\n')
