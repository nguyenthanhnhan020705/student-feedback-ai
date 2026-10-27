
import hashlib
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import joblib

from backend.config import MODEL_DIR


CONTRACT_VERSION = "1.0"

EXPECTED_FILES = {
    "sentiment": (
        "sentiment_pipeline.joblib",
        "sentiment_metadata.json",
    ),
    "topic": (
        "topic_pipeline.joblib",
        "topic_metadata.json",
    ),
}

EXPECTED_LABELS = {
    "sentiment": {"negative", "neutral", "positive"},
    "topic": {"lecturer", "curriculum", "facility", "other"},
}

REQUIRED_PACKAGES = (
    "numpy",
    "scipy",
    "pandas",
    "scikit-learn",
    "joblib",
)

MODEL_KEYS = {"nb", "logistic_regression", "linear_svm"}
PREPROCESSING_NAME = "ml.preprocessing.normalize_text"
PREPROCESSING_VERSION = "1.0"


def sha256_file(path: Path) -> str:
    """Tính SHA-256 của file theo từng khối dữ liệu."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    """Kiểm tra chuỗi SHA-256 gồm đúng 64 ký tự hex."""
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdefABCDEF" for char in value)
    )


class ModelService:
    def __init__(self, model_dir: str | Path = MODEL_DIR):
        self.model_dir = Path(model_dir)
        self.sentiment_model = None
        self.topic_model = None
        self.status = {
            "sentiment": "missing",
            "topic": "missing",
        }
        self.reload()

    @property
    def loaded(self) -> bool:
        return all(
            self.status[task] == "ready"
            for task in EXPECTED_FILES
        )

    def _current_package_versions(self) -> dict[str, str]:
        result = {}
        for package in REQUIRED_PACKAGES:
            try:
                result[package] = version(package)
            except PackageNotFoundError as exc:
                raise ValueError("Thiếu package cần thiết.") from exc
        return result

    def _validate_metadata(
        self,
        metadata: Any,
        task: str,
        artifact_name: str,
        artifact_path: Path,
    ) -> None:
        if not isinstance(metadata, dict):
            raise ValueError("Metadata không đúng cấu trúc.")

        expected_fields = {
            "contract_version",
            "task",
            "algorithm",
            "artifact_filename",
            "artifact_sha256",
            "labels",
            "python_version",
            "package_versions",
            "dataset_manifest_sha256",
            "preprocessing",
            "parameters",
            "selection",
            "trained_at",
        }
        if not expected_fields.issubset(metadata):
            raise ValueError("Metadata thiếu trường bắt buộc.")

        if metadata["contract_version"] != CONTRACT_VERSION:
            raise ValueError("Sai contract_version.")

        if metadata["task"] != task:
            raise ValueError("Sai task trong metadata.")

        algorithm = metadata["algorithm"]
        if not isinstance(algorithm, str) or algorithm not in MODEL_KEYS:
            raise ValueError("Thuật toán không hợp lệ.")

        if metadata["artifact_filename"] != artifact_name:
            raise ValueError("Sai tên artifact.")

        labels = metadata["labels"]
        if (
            not isinstance(labels, list)
            or any(not isinstance(label, str) for label in labels)
            or len(labels) != len(set(labels))
            or set(labels) != EXPECTED_LABELS[task]
        ):
            raise ValueError("Tập nhãn không hợp lệ.")

        expected_hash = metadata["artifact_sha256"]
        if not is_sha256(expected_hash):
            raise ValueError("Checksum trong metadata không hợp lệ.")

        if sha256_file(artifact_path).lower() != expected_hash.lower():
            raise ValueError("Checksum artifact không khớp.")

        dataset_hash = metadata["dataset_manifest_sha256"]
        if not is_sha256(dataset_hash):
            raise ValueError("Checksum dataset manifest không hợp lệ.")

        trained_python = metadata["python_version"]
        current_python = platform.python_version()
        if (
            not isinstance(trained_python, str)
            or ".".join(trained_python.split(".")[:2])
            != ".".join(current_python.split(".")[:2])
            or ".".join(current_python.split(".")[:2]) != "3.13"
        ):
            raise ValueError("Phiên bản Python không tương thích.")

        package_versions = metadata["package_versions"]
        if (
            not isinstance(package_versions, dict)
            or any(
                not isinstance(package_versions.get(package), str)
                for package in REQUIRED_PACKAGES
            )
        ):
            raise ValueError("package_versions không hợp lệ.")

        current_versions = self._current_package_versions()
        if any(
            package_versions[package] != current_versions[package]
            for package in REQUIRED_PACKAGES
        ):
            raise ValueError("Phiên bản package không tương thích.")

        preprocessing = metadata["preprocessing"]
        if (
            not isinstance(preprocessing, dict)
            or preprocessing.get("name") != PREPROCESSING_NAME
            or preprocessing.get("version") != PREPROCESSING_VERSION
        ):
            raise ValueError("Thông tin preprocessing không hợp lệ.")

        parameters = metadata["parameters"]
        if not isinstance(parameters, dict):
            raise ValueError("parameters không hợp lệ.")

        selection = metadata["selection"]
        if (
            not isinstance(selection, dict)
            or selection.get("algorithm") != algorithm
            or selection.get("metric") != "macro_f1"
            or not isinstance(selection.get("validation_metrics"), dict)
        ):
            raise ValueError("Thông tin selection không hợp lệ.")

        trained_at = metadata["trained_at"]
        if not isinstance(trained_at, str):
            raise ValueError("trained_at không hợp lệ.")

        try:
            timestamp = datetime.fromisoformat(
                trained_at.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError("trained_at không hợp lệ.") from exc

        if (
            timestamp.tzinfo is None
            or timestamp.utcoffset() != timezone.utc.utcoffset(timestamp)
        ):
            raise ValueError("trained_at phải ở múi giờ UTC.")

    def _load_one(self, task: str):
        artifact_name, metadata_name = EXPECTED_FILES[task]
        artifact_path = self.model_dir / artifact_name
        metadata_path = self.model_dir / metadata_name

        if not artifact_path.is_file() or not metadata_path.is_file():
            return "missing", None

        try:
            metadata = json.loads(
                metadata_path.read_text(encoding="utf-8")
            )
            self._validate_metadata(
                metadata,
                task,
                artifact_name,
                artifact_path,
            )

            # Chỉ nạp artifact từ nguồn đáng tin cậy.
            pipeline = joblib.load(artifact_path)

            classes = getattr(pipeline, "classes_", None)
            if classes is None:
                raise ValueError("Pipeline thiếu classes_.")

            class_values = list(classes)
            if (
                any(not isinstance(label, str) for label in class_values)
                or len(class_values) != len(set(class_values))
                or set(class_values) != EXPECTED_LABELS[task]
            ):
                raise ValueError("Tập class trong pipeline không hợp lệ.")

            if not callable(getattr(pipeline, "predict", None)):
                raise ValueError("Pipeline không có phương thức predict.")

            return "ready", pipeline

        except Exception:
            # Không đưa thông tin nội bộ hoặc stack trace ra API.
            return "invalid", None

    def reload(self) -> None:
        """Kiểm tra và nạp lại cả hai model."""
        self.sentiment_model = None
        self.topic_model = None
        self.status = {
            "sentiment": "missing",
            "topic": "missing",
        }

        sentiment_status, sentiment_model = self._load_one("sentiment")
        topic_status, topic_model = self._load_one("topic")

        self.status = {
            "sentiment": sentiment_status,
            "topic": topic_status,
        }

        # Chỉ sử dụng model khi cả hai task đều hợp lệ.
        if sentiment_status == "ready" and topic_status == "ready":
            self.sentiment_model = sentiment_model
            self.topic_model = topic_model

    def predict(self, text: str) -> dict[str, str]:
        if not self.loaded:
            raise RuntimeError("Models are not ready.")

        sentiment_result = self.sentiment_model.predict([text])
        topic_result = self.topic_model.predict([text])

        if len(sentiment_result) != 1 or len(topic_result) != 1:
            raise ValueError("Invalid prediction output.")

        sentiment_pred = sentiment_result[0]
        topic_pred = topic_result[0]

        if (
            not isinstance(sentiment_pred, str)
            or sentiment_pred not in EXPECTED_LABELS["sentiment"]
        ):
            raise ValueError("Invalid sentiment label.")

        if (
            not isinstance(topic_pred, str)
            or topic_pred not in EXPECTED_LABELS["topic"]
        ):
            raise ValueError("Invalid topic label.")

        return {
            "sentiment": sentiment_pred,
            "topic": topic_pred,
        }


model_service = ModelService()
