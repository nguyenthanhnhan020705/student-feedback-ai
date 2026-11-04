"""Strict v3 API, frozen-source readiness and no-fallback integration tests."""
import importlib.util
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


def components():
    assert importlib.util.find_spec('demo_v3.service') is not None, 'v3 service/API are missing'
    from demo_v3.service import Service
    from demo_v3.main import create_app
    return Service, create_app


@pytest.fixture(scope='module')
def live_service():
    Service, _ = components()
    service = Service()
    assert service.ready, service.status
    return service


@pytest.mark.parametrize('payload', [{},{'text':None},{'text':4},{'text':True},{'text':[]},
    {'text':' \t\n'},{'text':'a'*5001},{'text':' '+'a'*5000},{'text':'🙂'*5001},
    {'text':'Tốt','extra':1},{'text':'\ud800'},{'text':'\udfff'}])
def test_strict_input_before_readiness(payload):
    _, create_app = components()
    with TestClient(create_app(SimpleNamespace(ready=False,status={}))) as client:
        response=client.post('/api/v3/predict',content=json.dumps(payload).encode(),headers={'content-type':'application/json'})
    assert response.status_code==422
    assert response.json()['contract_version']=='3.0'
    assert response.json()['error']['code']=='INVALID_INPUT'


@pytest.mark.parametrize('body', [b'{',b'[]',b'null',b'{"text":"\xff"}',b'{"text":NaN}'])
def test_malformed_json_safe_envelope(body):
    _, create_app=components()
    with TestClient(create_app(SimpleNamespace(ready=False,status={}))) as client:
        response=client.post('/api/v3/predict',content=body,headers={'content-type':'application/json'})
    assert response.status_code==422
    assert response.json()['contract_version']=='3.0'


@pytest.mark.parametrize('text', ['🙂'*5000,' '+'a'*4999],ids=['emoji5000','raw5000'])
def test_raw_codepoint_boundary_is_preserved(text):
    _, create_app=components()
    received=[]
    def predict(raw):
        received.append(raw)
        return dict(contract_version='3.0',sentiment='undetermined',topic='other_domain')
    with TestClient(create_app(SimpleNamespace(ready=True,status={},predict=predict))) as client:
        assert client.post('/api/v3/predict',json={'text':text}).status_code==200
    assert received==[text]


def test_real_frozen_models_run_each_clause_without_fit(live_service,monkeypatch):
    _, create_app=components()
    calls=[]
    original=live_service.frozen.predict
    def inspect(text):
        calls.append(text)
        return original(text)
    monkeypatch.setattr(live_service.frozen,'predict',inspect)
    for pipe in live_service.frozen.models.values():
        def forbidden(*args,**kwargs):
            pytest.fail('fit is forbidden')
        monkeypatch.setattr(pipe,'fit',forbidden)
    result,audit=live_service.analyze('Thầy giảng rõ ràng; phòng học nóng.')
    assert result==dict(contract_version='3.0',sentiment='mixed',topic='education_quality',topics=['lecturer','facility'])
    assert calls==['Thầy giảng rõ ràng',' phòng học nóng']
    assert len(audit['clauses'])==2 and all(c['ct4']['contract_version']=='2.0' for c in audit['clauses'])
    assert audit['rules_version']=='experimental-1.0.0'
    with TestClient(create_app(live_service)) as client:
        response=client.post('/api/v3/predict',json={'text':'Môn học có ba tín chỉ.'})
    assert response.json()==dict(contract_version='3.0',sentiment='undetermined',topic='curriculum')


def test_old_ct4_neutral_never_creates_mixed():
    Service,_=components()
    class Frozen:
        ready=True
        status={'sentiment':'ready','topic':'ready'}
        def predict(self,text):
            return dict(contract_version='2.0',status='complete',sentiment={'status':'answered','label':'neutral','reason':None,'message':None},
                        topic={'status':'answered','label':'facility','reason':None,'message':None})
    result=Service(frozen=Frozen()).predict('Môn học có ba tín chỉ.')
    assert result['sentiment']=='undetermined' and result['topic']=='curriculum'


def test_ct4_failure_is_500_even_for_information_only(live_service,monkeypatch):
    _,create_app=components()
    def broken(text): raise ValueError('private-model-path')
    monkeypatch.setattr(live_service.frozen,'predict',broken)
    with TestClient(create_app(live_service)) as client:
        response=client.post('/api/v3/predict',json={'text':'🙂'})
    assert response.status_code==500
    assert response.json()['error']['code']=='INFERENCE_ERROR'
    assert 'sentiment' not in response.json() and 'private' not in response.text


@pytest.mark.parametrize('result', [dict(contract_version='2.0',sentiment='positive',topic='lecturer'),
    dict(contract_version='3.0',sentiment='neutral',topic='lecturer'),
    dict(contract_version='3.0',sentiment='positive',topic='other'),
    dict(contract_version='3.0',sentiment='positive',topic='lecturer',audit={})])
def test_invalid_service_outputs_are_errors(result):
    _,create_app=components()
    with TestClient(create_app(SimpleNamespace(ready=True,status={},predict=lambda _:result))) as client:
        response=client.post('/api/v3/predict',json={'text':'Tốt'})
    assert response.status_code==500 and 'sentiment' not in response.json()


@pytest.mark.parametrize('value', [None,[],{}, {'version':'wrong'},'not-json'])
def test_missing_or_invalid_rules_are_readiness_errors(tmp_path,value):
    Service,create_app=components()
    path=tmp_path/'rules.json'
    if value is not None: path.write_text(json.dumps(value),encoding='utf-8')
    service=Service(rules_path=path)
    assert not service.ready and service.status['rules']=='invalid'
    with TestClient(create_app(service)) as client:
        assert client.get('/api/health').json()['ready'] is False
        assert client.post('/api/v3/predict',json={'text':'Tốt'}).status_code==503


def copied_sources(tmp_path):
    for relative,names in [('.local-tools/ct4-augmentation/run-1', ['receipt.json']),
            ('.local-tools/ct4-augmentation/run-1/research-selected',
             [f'{t}_{s}' for t in ['sentiment','topic'] for s in ['pipeline.joblib','metadata.json']]),
            ('.local-tools/ct5-selective-prediction/run-1',['receipt.json','config.json','thresholds.json'])]:
        dest=tmp_path/relative;dest.mkdir(parents=True,exist_ok=True)
        for name in names: shutil.copyfile(ROOT/relative/name,dest/name)
    return tmp_path


@pytest.mark.parametrize('target', ['sentiment_pipeline.joblib','topic_metadata.json','ct4_receipt','ct5_receipt','config.json','thresholds.json','runtime'])
def test_frozen_provenance_and_runtime_failure_leave_api_startable(tmp_path,target,monkeypatch):
    Service,create_app=components()
    root=copied_sources(tmp_path)
    if target=='runtime':
        from backend.model_service import ModelService
        monkeypatch.setattr(ModelService,'_current_package_versions',lambda _:{})
    else:
        path=(root/'.local-tools/ct4-augmentation/run-1/research-selected'/target
              if target in ['sentiment_pipeline.joblib','topic_metadata.json']
              else root/'.local-tools/ct4-augmentation/run-1/receipt.json' if target=='ct4_receipt'
              else root/'.local-tools/ct5-selective-prediction/run-1'/('receipt.json' if target=='ct5_receipt' else target))
        path.write_bytes(b'null')
    service=Service(root=root)
    assert not service.ready
    with TestClient(create_app(service)) as client:
        assert client.get('/api/health').status_code==200
        assert client.post('/api/v3/predict',json={'text':'Tốt'}).status_code==503


def test_v3_assets_and_version(live_service):
    _,create_app=components()
    with TestClient(create_app(live_service)) as client:
        assert client.get('/api/health').json()['contract_version']=='3.0'
        assert client.post('/api/v2/predict',json={'text':'Tốt'}).status_code==404
        assert client.get('/rules.json').status_code==404
