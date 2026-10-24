
from fastapi import APIRouter

from backend.model_service import model_service

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "ready": model_service.loaded,
        "models": model_service.status,
        "contract_version": "1.0",
    }
