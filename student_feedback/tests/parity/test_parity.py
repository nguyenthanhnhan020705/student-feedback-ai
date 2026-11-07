"""Responses must equal the legacy demo_v3 app recorded by tools/capture_baseline.py."""
import base64
import io
import json
from pathlib import Path

import openpyxl
import pytest

pytestmark = pytest.mark.integration
CASES = json.loads((Path(__file__).with_name('baseline.json')).read_text(encoding='utf-8'))


def ids(kind):
    return [c for c in CASES if c['kind'] == kind]


def test_baseline_is_nontrivial():
    kinds = {c['kind'] for c in CASES}
    assert kinds == {'health', 'predict', 'predict_raw', 'analyze_row', 'import', 'export'}
    assert len(CASES) >= 30


def test_health(real_client):
    assert real_client.get('/api/health').json() == ids('health')[0]['response']


@pytest.mark.parametrize('case', ids('predict'), ids=lambda c: repr(c['text'])[:30])
def test_predict(real_client, case):
    if 'client_error' in case:
        with pytest.raises(Exception):
            real_client.post('/api/v3/predict', json={'text': case['text']})
        return
    response = real_client.post('/api/v3/predict', json={'text': case['text']})
    assert (response.status_code, response.json()) == (case['status'], case['body'])


@pytest.mark.parametrize('case', ids('predict_raw'), ids=lambda c: c['raw'])
def test_predict_raw(real_client, case):
    response = real_client.post('/api/v3/predict', content=base64.b64decode(case['raw']), headers={'content-type': 'application/json'})
    assert (response.status_code, response.json()) == (case['status'], case['body'])


@pytest.mark.parametrize('case', ids('analyze_row'), ids=lambda c: repr(c['text'])[:30])
def test_analyze_row(real_client, case):
    response = real_client.post('/api/v3/analyze-row', json={'text': case['text']})
    assert (response.status_code, response.json()) == (case['status'], case['body'])


@pytest.mark.parametrize('case', ids('import'), ids=lambda c: c['filename'])
def test_import(real_client, case):
    response = real_client.post('/api/v3/import', params={'filename': case['filename']}, content=base64.b64decode(case['raw']))
    assert (response.status_code, response.json()) == (case['status'], case['body'])


def test_export_semantics(real_client):
    case = ids('export')[0]
    response = real_client.post('/api/v3/export', json=case['request'])
    assert response.status_code == case['status']
    assert response.headers['content-disposition'] == case['disposition']
    book = openpyxl.load_workbook(io.BytesIO(response.content))
    got = {ws.title: [[[c.value, c.data_type] for c in row] for row in ws.iter_rows()] for ws in book.worksheets}
    assert got == json.loads(json.dumps(case['sheets']))
