from fastapi import APIRouter
from backend.schemas import HealthResponse
from backend.model_service import model_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "ok",
        "model_loaded": model_service.loaded,
        "models": {
            "sentiment": model_service.sentiment_model is not None,
            "topic": model_service.topic_model is not None
        }
    }