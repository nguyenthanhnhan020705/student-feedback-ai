
from pathlib import Path
import hashlib
import json

import pandas as pd

from ml.preprocessing import normalize_text


DATA_DIR = Path("data/raw")
SPLITS = ("train", "valid", "test")
LABELS = {"positive", "negative", "neutral"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_split(split: str, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    if split not in SPLITS:
        raise ValueError(f"Split không hợp lệ: {split}")

    path = data_dir / f"UIT-VSFC_{split}.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")

    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    if list(df.columns) != ["text", "label"]:
        raise ValueError(
            f"{path}: cần đúng hai cột text,label; "
            f"thực tế là {list(df.columns)}"
        )

    df["text"] = df["text"].map(normalize_text)
    df["label"] = df["label"].str.strip().str.lower()

    
    empty_text = df["text"].str.strip().eq("")
    empty_label = df["label"].str.strip().eq("")

    if empty_text.any():
        rows = (df.index[empty_text] + 2).tolist()
        raise ValueError(
            f"{path}: text rỗng ở dòng CSV {rows[:10]}"
    )

    if empty_label.any():
        rows = (df.index[empty_label] + 2).tolist()
        raise ValueError(
            f"{path}: label rỗng ở dòng CSV {rows[:10]}"
    )

    if (df["label"] == "").any():
        rows = (df.index[df["label"] == ""] + 2).tolist()
        raise ValueError(f"{path}: label rỗng ở dòng CSV {rows[:10]}")

    unknown = sorted(set(df["label"]) - LABELS)
    if unknown:
        raise ValueError(f"{path}: nhãn không hợp lệ: {unknown}")

    return df


def load_all(data_dir: Path = DATA_DIR) -> dict[str, pd.DataFrame]:
    """Đọc các split gốc, không tự chia lại dữ liệu."""
    return {split: load_split(split, data_dir) for split in SPLITS}



def inspect_data(data_dir: Path = DATA_DIR) -> dict:
    """Thống kê dữ liệu gốc, ghi nhận lỗi và phát hiện trùng lặp."""
    report = {
        "source_dir": str(data_dir),
        "splits": {},
        "duplicates": {
            "within_split": {},
            "across_splits": [],
        },
        "data_quality": {},
        "policy": {
            "duplicates": "Report only; do not automatically remove",
            "split_membership": "Preserve original train/valid/test",
            "text_normalization": "Unicode NFC and whitespace only",
            "empty_records": "Report only; do not modify source CSV",
        },
    }

    text_sets = {}

    for split in SPLITS:
        path = data_dir / f"UIT-VSFC_{split}.csv"

        if not path.is_file():
            raise FileNotFoundError(f"Không tìm thấy file: {path}")

        # Đọc dữ liệu để kiểm tra chất lượng, không gọi load_split()
        # vì load_split() chủ động báo lỗi khi gặp bản ghi không hợp lệ.
        df = pd.read_csv(path, dtype=str, keep_default_na=False)

        if list(df.columns) != ["text", "label"]:
            raise ValueError(
                f"{path}: cần đúng hai cột text,label; "
                f"thực tế là {list(df.columns)}"
            )

        raw_text = df["text"].map(normalize_text)
        raw_label = df["label"].str.strip().str.lower()

        empty_text = raw_text.str.strip().eq("")
        empty_label = raw_label.eq("")
        unknown_label = ~raw_label.isin(LABELS) & ~empty_label
        invalid = empty_text | empty_label | unknown_label

        report["data_quality"][split] = {
            "source_rows": int(len(df)),
            "empty_text_rows": int(empty_text.sum()),
            "empty_label_rows": int(empty_label.sum()),
            "unknown_label_rows": int(unknown_label.sum()),
            "invalid_rows": int(invalid.sum()),
            "invalid_csv_lines": (
                df.index[invalid] + 2
            ).tolist(),
        }

        # Chỉ dùng các bản ghi hợp lệ để tính thống kê nội dung.
        # Không xóa hay sửa bất kỳ dòng nào trong CSV gốc.
        valid = pd.DataFrame({
            "text": raw_text,
            "label": raw_label,
        }).loc[~invalid].copy()

        counts = valid["label"].value_counts().to_dict()

        report["splits"][split] = {
            "rows": int(len(valid)),
            "label_counts": {k: int(v) for k, v in counts.items()},
            "unique_texts": int(valid["text"].nunique()),
            "duplicate_rows": int(
                valid["text"].duplicated(keep=False).sum()
            ),
            "file_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }

        report["duplicates"]["within_split"][split] = (
            valid.loc[
                valid["text"].duplicated(keep=False), "text"
            ].value_counts().to_dict()
        )
        text_sets[split] = set(valid["text"])

    for i, left in enumerate(SPLITS):
        for right in SPLITS[i + 1:]:
            overlap = text_sets[left] & text_sets[right]
            report["duplicates"]["across_splits"].append({
                "split_a": left,
                "split_b": right,
                "overlap_unique_texts": len(overlap),
                "examples": sorted(overlap)[:10],
            })

    return report



def write_manifest(
    output_path: Path = Path("reports/data/manifest.json"),
    data_dir: Path = DATA_DIR,
) -> dict:
    report = inspect_data(data_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


if __name__ == "__main__":
    result = write_manifest()
    print(json.dumps(result, ensure_ascii=False, indent=2))
