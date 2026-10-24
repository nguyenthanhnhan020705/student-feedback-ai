from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Schema cho GET /api/health
class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    models: dict[str, bool]

# Schema cho Request POST /api/predict
class PredictRequest(BaseModel):
    text: str = Field(..., description="Câu phản hồi sinh viên cần dự đoán")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Chuỗi đầu vào không được để rỗng hoặc chỉ chứa khoảng trắng.")
        if len(v) > 5000:
            raise ValueError("Chuỗi đầu vào vượt quá giới hạn 5000 ký tự.")
        return v

# Schema cho Response POST /api/predict thành công
class PredictResponse(BaseModel):
    text: str
    sentiment: str
    topic: str

# Schema hiển thị lỗi chuẩn
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[list] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail