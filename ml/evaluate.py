"""TV3/TV4: implement held-out test evaluation, not model selection."""

import argparse
from pathlib import Path


def evaluate(model_path: Path, test_path: Path, report_path: Path) -> None:
    """Export real metrics per docs/API_CONTRACT.md once implemented."""
    raise NotImplementedError(
        'Chua trien khai evaluation. Can pipeline da train va tap test doc lap; '
        'khong tao Accuracy/F1 hoac confusion matrix gia.'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description='Khung danh gia ML; chua trien khai.')
    parser.add_argument('--model', type=Path, default=Path('models/sentiment_pipeline.joblib'))
    parser.add_argument('--test', type=Path, default=Path('data/processed/test.csv'))
    parser.add_argument('--report', type=Path, default=Path('reports/metrics_sentiment.json'))
    args = parser.parse_args()
    try:
        evaluate(args.model, args.test, args.report)
    except NotImplementedError as exc:
        parser.exit(2, f'{exc}\n')


if __name__ == '__main__':
    main()
