import numpy as np
import pytest


def test_partial_or_corrupt_models_not_ready(tmp_path, monkeypatch):
    from backend.model_service import ModelService

    paths = {task: tmp_path / f'{task}.joblib' for task in ('sentiment', 'topic')}
    paths['sentiment'].write_bytes(b'not a model')
    service = ModelService(paths)
    service.load()
    assert service.models_loaded == {'sentiment': False, 'topic': False}
    assert service.errors['sentiment']
    monkeypatch.setattr('backend.model_service.joblib.load', lambda path: object())
    service.load()
    assert service.models_loaded['sentiment'] is False


@pytest.mark.parametrize('codes', [[99], [0.5], ['positive'], [True], [], [0, 1], [[0]]])
def test_invalid_model_output_rejected(codes):
    from ml.inference import predict_codes

    class PipelineStub:
        def predict(self, texts):
            return codes

    with pytest.raises(ValueError):
        predict_codes(PipelineStub(), ['input'], 'sentiment')


def test_numpy_integer_labels_accepted():
    from ml.inference import predict_codes

    class PipelineStub:
        def predict(self, texts):
            return np.array([2], dtype=np.int64)

    assert predict_codes(PipelineStub(), ['input'], 'sentiment') == [2]


def test_service_uses_real_predict_and_preserves_partial_load(tmp_path, monkeypatch):
    from backend.model_service import ModelService, ModelUnavailable

    class PipelineStub:
        def predict(self, texts):
            return [0] * len(texts)

    paths = {task: tmp_path / f'{task}.joblib' for task in ('sentiment', 'topic')}
    paths['sentiment'].touch()
    monkeypatch.setattr('backend.model_service.joblib.load', lambda path: PipelineStub())
    service = ModelService(paths)
    service.load()
    assert service.models_loaded == {'sentiment': True, 'topic': False}
    with pytest.raises(ModelUnavailable):
        service.predict(['text'])


def test_model_prediction_error_returns_503(tmp_path, monkeypatch):
    from backend.main import create_app
    from backend.model_service import ModelService
    from fastapi.testclient import TestClient

    class BrokenPipeline:
        def predict(self, texts):
            raise RuntimeError('incompatible vectorizer')

    paths = {task: tmp_path / f'{task}.joblib' for task in ('sentiment', 'topic')}
    for path in paths.values():
        path.touch()
    monkeypatch.setattr('backend.model_service.joblib.load', lambda path: BrokenPipeline())
    with TestClient(create_app(ModelService(paths), tmp_path)) as client:
        response = client.post('/api/predict', json={'text': 'test input'})
        assert response.status_code == 503
        assert 'detail' in response.json()
