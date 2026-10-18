"""Load trusted local joblib artifacts once per application startup."""

import logging
import os
from pathlib import Path

import joblib

from ml.inference import predict_codes
from ml.labels import LABELS

ROOT = Path(__file__).resolve().parents[1]
logger = logging.getLogger(__name__)


class ModelUnavailable(RuntimeError):
    """No valid pair of pipelines is available for prediction."""


class ModelService:
    def __init__(self, paths: dict[str, Path] | None = None):
        configured = paths if paths is not None else {
            task: Path(os.environ.get(f'{task.upper()}_MODEL_PATH',
                                      f'models/{task}_pipeline.joblib'))
            for task in LABELS
        }
        self.paths = {
            task: path if (path := Path(configured[task])).is_absolute() else ROOT / path
            for task in LABELS
        }
        self.pipelines = {}
        self.errors: dict[str, str] = {}

    def load(self) -> None:
        self.pipelines.clear()
        self.errors.clear()
        for task, path in self.paths.items():
            if not path.is_file():
                self.errors[task] = 'Chưa có file mô hình.'
                continue
            try:
                pipeline = joblib.load(path)
                if not callable(getattr(pipeline, 'predict', None)):
                    raise ValueError('Artifact has no predict method')
                self.pipelines[task] = pipeline
            except Exception:
                logger.exception('Cannot load trusted %s model', task)
                self.errors[task] = 'Không tải được mô hình. Kiểm tra pipeline và phiên bản thư viện.'

    @property
    def models_loaded(self) -> dict[str, bool]:
        return {task: task in self.pipelines for task in LABELS}

    def predict(self, texts: list[str]) -> list[dict]:
        if not all(self.models_loaded.values()):
            raise ModelUnavailable(
                'Mô hình chưa sẵn sàng. Cần hai pipeline sentiment và topic hợp lệ; '
                'hãy bổ sung mô hình thật và khởi động lại ứng dụng.'
            )
        codes = {}
        for task in LABELS:
            try:
                codes[task] = predict_codes(self.pipelines[task], texts, task)
            except Exception as exc:
                logger.exception('Prediction failed for %s', task)
                self.pipelines.pop(task, None)
                self.errors[task] = 'Mô hình lỗi khi dự đoán; cần kiểm tra và khởi động lại.'
                raise ModelUnavailable(self.errors[task]) from exc
        results = []
        for index, text in enumerate(texts):
            result = {'text': text}
            for task in LABELS:
                code = codes[task][index]
                label, label_vi = LABELS[task][code]
                result[task] = {'code': code, 'label': label, 'label_vi': label_vi}
            results.append(result)
        return results
