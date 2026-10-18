"""HTTP schemas shared with OpenAPI; keep in sync with docs/API_CONTRACT.md."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator

MAX_TEXT_LENGTH = 5000


class PredictRequest(BaseModel):
    text: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=MAX_TEXT_LENGTH)]

    @field_validator('text')
    @classmethod
    def meaningful_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('Vui lòng nhập phản hồi có nội dung, không chỉ khoảng trắng.')
        return value


class LabelResult(BaseModel):
    code: int
    label: str
    label_vi: str


class PredictResponse(BaseModel):
    text: str
    sentiment: LabelResult
    topic: LabelResult


class BatchRow(BaseModel):
    text: str
    sentiment: str
    topic: str


class BatchSummary(BaseModel):
    sentiment: dict[str, int]
    topic: dict[str, int]


class BatchResponse(BaseModel):
    total: int
    results: list[BatchRow]
    summary: BatchSummary


class HealthResponse(BaseModel):
    status: Literal['ready', 'setup_required']
    models_loaded: dict[str, bool]


class MetricsResponse(BaseModel):
    available: bool
    sentiment: dict
    topic: dict


class ErrorResponse(BaseModel):
    detail: str


ERROR_RESPONSES = {
    503: {'model': ErrorResponse, 'description': 'Mô hình chưa sẵn sàng hoặc suy luận lỗi.'},
}
