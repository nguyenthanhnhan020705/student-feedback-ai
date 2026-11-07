import pytest


def test_missing_bundle_keeps_ui_available(tmp_path):
    from fastapi.testclient import TestClient
    from feedback_ai.config import Settings
    from feedback_ai.api.app import create_app
    with TestClient(create_app(Settings.from_root(tmp_path))) as client:
        assert client.get('/').status_code == 200
        assert client.get('/api/health').json()['ready'] is False
        assert client.post('/api/v3/predict', json={'text':'Tốt'}).status_code == 503
        assert client.post('/api/v3/predict', json={'text':' '}).status_code == 422
        assert client.get('/mau-phan-hoi.xlsx').status_code == 200


def test_file_import_preserves_rows():
    from feedback_ai.io.imports import parse_upload
    result=parse_upload('input.csv',b'text\n"a\nb"\na\na\n')
    assert result['sheets'][0]['rows']==[['a\nb'],['a'],['a']]


def test_mixed_evidence():
    from feedback_ai.inference.detector import Detector
    from feedback_ai.inference.ontology import aggregate
    e=Detector().detect('Giảng viên nhiệt tình nhưng phòng học nóng.')
    assert aggregate(e.positive,e.negative,e.topics)=={'sentiment':'mixed','topic':'education_quality'}


def test_manifest_blocks_escape(tmp_path):
    import json
    from feedback_ai.inference.bundle import verify_manifest
    path=tmp_path/'manifest.json'
    path.write_text(json.dumps({'files':{'../outside':'a'*64}}))
    with pytest.raises(ValueError):
        verify_manifest(path)
