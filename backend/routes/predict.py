
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.schemas import PredictRequest, PredictResponse, ErrorResponse
from backend.model_service import model_service

router = APIRouter()

SENTIMENT_LABELS = {"negative", "neutral", "positive"}
TOPIC_LABELS = {"lecturer", "curriculum", "facility", "other"}


def error_response(
    status_code: int,
    code: str,
    message: str,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": [],
            },
            "contract_version": "1.0",
        },
    )


@router.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def predict_feedback(request: PredictRequest):
    if not model_service.loaded:
        return error_response(
            503,
            "MODEL_NOT_READY",
            "Mô hình dự đoán chưa sẵn sàng.",
        )

    try:
        result = model_service.predict(request.text)
    except Exception:
        return error_response(
            500,
            "INFERENCE_ERROR",
            "Không thể thực hiện dự đoán.",
        )

    if (
        not isinstance(result, dict)
        or result.get("sentiment") not in SENTIMENT_LABELS
        or result.get("topic") not in TOPIC_LABELS
    ):
        return error_response(
            500,
            "INFERENCE_ERROR",
            "Mô hình trả về kết quả không hợp lệ.",
        )

    try:
        return {
            "sentiment": result["sentiment"],
            "topic": result["topic"],
            "contract_version": "1.0",
        }
    except Exception:
        return error_response(
            500,
            "INTERNAL_ERROR",
            "Đã xảy ra lỗi nội bộ.",
        )
