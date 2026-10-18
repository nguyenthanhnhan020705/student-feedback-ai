import json

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path):
    from backend.main import create_app
    from backend.model_service import ModelService

    paths = {task: tmp_path / f'{task}.joblib' for task in ('sentiment', 'topic')}
    with TestClient(create_app(ModelService(paths), tmp_path)) as test_client:
        yield test_client


def upload(client, content, name='feedback.csv'):
    if isinstance(content, str):
        content = content.encode('utf-8')
    return client.post('/api/predict-batch', files={'file': (name, content, 'text/csv')})


def test_health_reports_actual_missing_models(client):
    assert client.get('/api/health').json() == {
        'status': 'setup_required', 'models_loaded': {'sentiment': False, 'topic': False}
    }


def test_missing_model_never_returns_predictions(client):
    response = client.post('/api/predict', json={'text': 'Giảng viên nhiệt tình.'})
    assert response.status_code == 503
    assert 'detail' in response.json()
    assert upload(client, 'text\nGiảng viên nhiệt tình.').status_code == 503


@pytest.mark.parametrize('payload', [{}, {'text': ''}, {'text': ' \t\n'}, {'text': 123},
                                     {'text': None}, {'text': 'a' * 5001}])
def test_invalid_text_returns_422_even_without_models(client, payload):
    assert client.post('/api/predict', json=payload).status_code == 422


@pytest.mark.parametrize('content', [b'', b'text\n', b'wrong\nx', b'text\n"  "',
                                     b'text\n\xff', b'text\n"unterminated',
                                     b'text,text\na,b', b'text\na,b', b'text\n""',
                                     ('text\n' + 'a' * 5001).encode()])
def test_invalid_csv_returns_422(client, content):
    assert upload(client, content).status_code == 422


def test_csv_limits(client):
    assert upload(client, b'text\n' + b'a\n' * 1001).status_code == 422
    assert upload(client, b'x' * (2 * 1024 * 1024 + 1)).status_code == 413
    assert upload(client, 'text\na', 'file.txt').status_code == 422
    assert client.post('/api/predict-batch').status_code == 422


def test_metrics_missing_placeholder_and_corrupt_are_not_scores(client, tmp_path):
    result = client.get('/api/metrics').json()
    assert result['available'] is False
    for task in ('sentiment', 'topic'):
        (tmp_path / f'metrics_{task}.json').write_text('{"available":false}', encoding='utf-8')
    assert client.get('/api/metrics').json()['available'] is False
    (tmp_path / 'metrics_sentiment.json').write_text('{broken', encoding='utf-8')
    result = client.get('/api/metrics').json()
    assert result['available'] is False
    assert result['sentiment']['error']


def test_valid_metrics_are_read_from_disk(client, tmp_path):
    # Fixture values test serialization only; never bundled as an experiment report.
    report = {'available': True, 'model': 'test-fixture', 'split': 'test',
              'accuracy': 0.4, 'precision_macro': 0.3, 'recall_macro': 0.2,
              'f1_macro': 0.1, 'confusion_matrix': [[1, 2], [3, 4]]}
    for task in ('sentiment', 'topic'):
        (tmp_path / f'metrics_{task}.json').write_text(json.dumps(report), encoding='utf-8')
    result = client.get('/api/metrics').json()
    assert result['available'] is True
    assert result['sentiment'] == report


def test_incomplete_metrics_do_not_become_available(client, tmp_path):
    (tmp_path / 'metrics_sentiment.json').write_text('{"available":true}', encoding='utf-8')
    result = client.get('/api/metrics').json()
    assert result['sentiment']['available'] is False


def test_overflowing_number_inside_optional_metrics_field_is_not_a_server_error(client, tmp_path):
    report = ('{"available":true,"model":"test-fixture","split":"test",'
              '"accuracy":0.4,"precision_macro":0.3,"recall_macro":0.2,'
              '"f1_macro":0.1,"confusion_matrix":[[1,2],[3,4]],'
              '"comparison":[{"f1_macro":1e999}]}')
    (tmp_path / 'metrics_sentiment.json').write_text(report, encoding='utf-8')
    response = client.get('/api/metrics')
    assert response.status_code == 200
    assert response.json()['sentiment']['available'] is False
    assert response.json()['sentiment']['error']


def test_pages_assets_and_openapi(client):
    assert 'Phân tích AI' in client.get('/').text
    for path in ('/static/style.css', '/static/app.js', '/docs'):
        assert client.get(path).status_code == 200
    schema = client.get('/openapi.json').json()
    for path in ('/api/health', '/api/predict', '/api/predict-batch', '/api/metrics'):
        assert path in schema['paths']
    assert 'multipart/form-data' in schema['paths']['/api/predict-batch']['post']['requestBody']['content']


@pytest.fixture
def ready_client(tmp_path, monkeypatch):
    from backend.main import create_app
    from backend.model_service import ModelService

    # Test-only pipeline substitutes; no model file is generated or trained.
    class PipelineStub:
        def __init__(self, code):
            self.code = code

        def predict(self, texts):
            return [self.code] * len(texts)

    paths = {task: tmp_path / f'{task}.joblib' for task in ('sentiment', 'topic')}
    for path in paths.values():
        path.touch()
    monkeypatch.setattr('backend.model_service.joblib.load',
                        lambda path: PipelineStub(2 if path == paths['sentiment'] else 0))
    with TestClient(create_app(ModelService(paths), tmp_path)) as test_client:
        yield test_client


def test_prediction_contract_using_test_only_pipeline(ready_client):
    assert ready_client.get('/api/health').json()['status'] == 'ready'
    response = ready_client.post('/api/predict', json={'text': 'Một phản hồi kiểm thử'})
    assert response.status_code == 200
    assert response.json() == {
        'text': 'Một phản hồi kiểm thử',
        'sentiment': {'code': 2, 'label': 'positive', 'label_vi': 'Tích cực'},
        'topic': {'code': 0, 'label': 'lecturer', 'label_vi': 'Giảng viên'},
    }


def test_batch_bom_quotes_and_summary_using_test_only_pipeline(ready_client):
    response = upload(ready_client, '\ufefftext\n"Câu một, có dấu phẩy"\n"Câu hai\nxuống dòng"')
    assert response.status_code == 200
    result = response.json()
    assert result['total'] == 2
    assert result['results'][0]['text'] == 'Câu một, có dấu phẩy'
    assert result['results'][0]['sentiment'] == 'positive'
    assert result['summary']['sentiment'] == {'negative': 0, 'neutral': 0, 'positive': 2}
    assert sum(result['summary']['topic'].values()) == 2


def test_exact_row_and_text_limits_accepted(ready_client):
    assert upload(ready_client, 'text\n' + 'a\n' * 1000).json()['total'] == 1000
    assert ready_client.post('/api/predict', json={'text': 'a' * 5000}).status_code == 200
