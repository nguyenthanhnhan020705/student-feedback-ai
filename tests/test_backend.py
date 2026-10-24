import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data

def test_predict_model_not_ready():
    response = client.post("/api/predict", json={"text": "Giảng viên dạy rất tâm huyết"})
    assert response.status_code == 503
    data = response.json()
    assert data["detail"]["error"]["code"] == "MODEL_NOT_READY"

def test_predict_empty_text():
    response = client.post("/api/predict", json={"text": "   "})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_predict_exceed_length():
    long_text = "a" * 5001
    response = client.post("/api/predict", json={"text": long_text})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"