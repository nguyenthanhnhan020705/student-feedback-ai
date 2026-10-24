
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator


class HealthResponse(BaseModel):
    status: Literal["ok"]
    ready: bool
    models: dict[str, Literal["ready", "missing", "invalid"]]
    contract_version: Literal["1.0"]


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: StrictStr = Field(
        ...,
        description="Câu phản hồi sinh viên cần dự đoán",
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        # Kiểm tra độ dài trước khi kiểm tra chuỗi rỗng.
        if len(value) > 5000:
            raise ValueError("too_long")

        if not value.strip():
            raise ValueError("blank")

        # Giữ nguyên nội dung gốc, không strip hoặc chuẩn hóa.
        return value


class PredictResponse(BaseModel):
    sentiment: Literal["negative", "neutral", "positive"]
    topic: Literal["lecturer", "curriculum", "facility", "other"]
    contract_version: Literal["1.0"]


class ErrorDetailItem(BaseModel):
    field: str
    reason: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[ErrorDetailItem]


class ErrorResponse(BaseModel):
    error: ErrorDetail
    contract_version: Literal["1.0"]
