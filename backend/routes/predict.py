from fastapi import APIRouter, HTTPException, status
from backend.schemas import PredictRequest, PredictResponse, ErrorResponse
from backend.model_service import model_service

router = APIRouter()

@router.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        503: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    }
)
def predict_feedback(request: PredictRequest):
    if not model_service.loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "code": "MODEL_NOT_READY",
                    "message": "Mô hình dự đoán chưa được nạp hoặc file artifact bị thiếu.",
                    "details": None
                }
            }
        )
    result = model_service.predict(request.text)
    return result