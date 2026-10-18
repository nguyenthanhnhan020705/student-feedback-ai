"""TV4: implement NB/LR/LinearSVC comparison using train + validation."""

from pathlib import Path


def train(data_dir: Path, output: Path, seed: int = 42) -> None:
    """Save one full text pipeline only after real experiments."""
    raise NotImplementedError(
        'Chua trien khai training topic. TV2/TV4 can xac minh du lieu, nhan '
        'va hoan thien so sanh NB/LR/LinearSVC. Khong tao model hoac metrics.'
    )


if __name__ == '__main__':
    from ml.scaffold import training_cli
    training_cli('topic')
