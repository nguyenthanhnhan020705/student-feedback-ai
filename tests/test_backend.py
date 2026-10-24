
from fastapi.testclient import TestClient
from unittest.mock import patch, PropertyMock

from backend.main import app
from backend.model_service import ModelService

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["ready"] is False
    assert data["models"] == {
        "sentiment": "missing",
        "topic": "missing",
    }
    assert data["contract_version"] == "1.0"


def test_predict_model_not_ready():
    response = client.post(
        "/api/predict",
        json={"text": "Giảng viên dạy rất tâm huyết"},
    )

    assert response.status_code == 503
    data = response.json()

    assert data["error"]["code"] == "MODEL_NOT_READY"
    assert data["error"]["details"] == []
    assert data["contract_version"] == "1.0"


def test_predict_empty_text():
    response = client.post(
        "/api/predict",
        json={"text": "   "},
    )

    assert response.status_code == 422
    data = response.json()

    assert data["error"]["code"] == "INVALID_INPUT"
    assert data["error"]["details"] == [
        {"field": "text", "reason": "blank"}
    ]
    assert data["contract_version"] == "1.0"


def test_predict_exceed_length():
    response = client.post(
        "/api/predict",
        json={"text": "a" * 5001},
    )

    assert response.status_code == 422
    data = response.json()

    assert data["error"]["code"] == "INVALID_INPUT"
    assert data["error"]["details"] == [
        {"field": "text", "reason": "too_long"}
    ]
    assert data["contract_version"] == "1.0"


def test_predict_missing_text():
    response = client.post("/api/predict", json={})

    assert response.status_code == 422
    data = response.json()

    assert data["error"]["code"] == "INVALID_INPUT"
    assert data["error"]["details"] == [
        {"field": "text", "reason": "required"}
    ]
    assert data["contract_version"] == "1.0"


def test_predict_wrong_text_type():
    response = client.post(
        "/api/predict",
        json={"text": 123},
    )

    assert response.status_code == 422
    data = response.json()

    assert data["error"]["code"] == "INVALID_INPUT"
    assert data["error"]["details"] == [
        {"field": "text", "reason": "type"}
    ]


def test_predict_extra_field():
    response = client.post(
        "/api/predict",
        json={"text": "Giảng viên dạy tốt", "extra": "unexpected"},
    )

    assert response.status_code == 422
    data = response.json()

    assert data["error"]["code"] == "INVALID_INPUT"
    assert data["error"]["details"] == [
        {"field": "extra", "reason": "extra_field"}
    ]


def test_predict_invalid_json():
    response = client.post(
        "/api/predict",
        content="{",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    data = response.json()

    assert data["error"]["code"] == "INVALID_INPUT"
    assert data["error"]["details"] == [
        {"field": "$body", "reason": "invalid_json"}
    ]
    assert data["contract_version"] == "1.0"


def test_predict_inference_error():
    with (
        patch.object(
            ModelService,
            "loaded",
            new_callable=PropertyMock,
            return_value=True,
        ),
        patch(
            "backend.routes.predict.model_service.predict",
            side_effect=RuntimeError("simulated inference failure"),
        ),
    ):
        response = client.post(
            "/api/predict",
            json={"text": "Giảng viên dạy rất tốt"},
        )

    assert response.status_code == 500
    data = response.json()

    assert data["error"]["code"] == "INFERENCE_ERROR"
    assert data["error"]["details"] == []
    assert data["contract_version"] == "1.0"
    assert "sentiment" not in data
    assert "topic" not in data
