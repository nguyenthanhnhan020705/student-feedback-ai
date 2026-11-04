"""Browser acceptance. Error routes are controlled fixtures, real inference is separate."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.browser


@pytest.fixture(scope='module')
def server_url():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    url = f'http://127.0.0.1:{port}'
    env = dict(os.environ, SFAI_MODEL_DIR=str(ROOT / 'models'))
    process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', str(port)], cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if process.poll() is not None:
                pytest.fail('Demo server exited during startup')
            try:
                with urllib.request.urlopen(url + '/api/health', timeout=1) as response:
                    assert json.load(response)['ready'] is True
                break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail('Demo server did not start')
        yield url
    finally:
        process.terminate()
        process.wait(timeout=10)


@pytest.fixture(scope='module', params=['chrome', 'msedge'])
def browser_instance(request):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel=request.param)
        yield browser, request.param
        browser.close()


@pytest.fixture
def ui(browser_instance, server_url):
    browser, name = browser_instance
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = context.new_page()
    page.set_default_timeout(15000)
    page.goto(server_url)
    page.wait_for_function("document.getElementById('health').textContent === 'Mô hình sẵn sàng'")
    yield page, name, server_url
    context.close()


def test_real_inference_and_screenshot(ui, browser_instance):
    from playwright.sync_api import expect
    page, name, url = ui
    text = 'Giảng viên giải thích rất dễ hiểu.'
    expect(page.locator('h1')).to_have_text('Phân tích phản hồi sinh viên')
    page.locator('#text').fill(text)
    with page.expect_response('**/api/predict') as response:
        page.locator('#go').click()
    result = response.value.json()
    assert result['contract_version'] == '1.0'
    labels = {'negative': 'Tiêu cực', 'neutral': 'Trung tính', 'positive': 'Tích cực', 'lecturer': 'Giảng viên', 'curriculum': 'Chương trình đào tạo', 'facility': 'Cơ sở vật chất', 'other': 'Khác'}
    expect(page.locator('#out .res b')).to_have_text([labels[result['sentiment']], labels[result['topic']]])
    expect(page.locator('#mockBanner')).to_be_hidden()
    evidence = ROOT / 'reports/evidence/frontend'
    evidence.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(evidence / f'{name}-real-prediction.png'), full_page=True)
    (evidence / f'{name}-real-prediction.json').write_text(json.dumps({'browser': name, 'version': browser_instance[0].version, 'input': text, 'response': result, 'fixture': False}, ensure_ascii=False, indent=2), encoding='utf-8')


def test_unicode_boundaries_and_blank_input(ui):
    from playwright.sync_api import expect
    page, _, _ = ui
    page.locator('#text').fill('  \n\t')
    expect(page.locator('#go')).to_be_disabled()
    page.locator('#text').fill('🙂' * 5000)
    expect(page.locator('#count')).to_have_text('5000 / 5000')
    expect(page.locator('#go')).to_be_enabled()
    page.locator('#text').fill('🙂' * 5001)
    expect(page.locator('#go')).to_be_disabled()


@pytest.mark.parametrize('status', [422, 503, 500])
def test_error_retains_input_and_clears_old_result(ui, status):
    from playwright.sync_api import expect
    page, _, _ = ui
    page.locator('#text').fill('Giảng viên rất tận tình.')
    page.locator('#go').click()
    expect(page.locator('#out .res')).to_be_visible()
    page.route('**/api/predict', lambda route: route.fulfill(status=status, content_type='application/json', body=json.dumps({'error': {'code': {422:'INVALID_INPUT',503:'MODEL_NOT_READY',500:'INTERNAL_ERROR'}[status], 'message':'fixture error', 'details':[]}, 'contract_version':'1.0'})))
    page.locator('#go').click()
    expect(page.locator('#out .res')).to_have_count(0)
    expect(page.locator('#out p')).to_have_class('warn' if status == 503 else 'err')
    expect(page.locator('#text')).to_have_value('Giảng viên rất tận tình.')
    if status == 503:
        expect(page.locator('#go')).to_be_disabled()
        page.locator('#recheck').click()
        expect(page.locator('#go')).to_be_enabled()


def test_network_failure_and_retry(ui):
    from playwright.sync_api import expect
    page, _, _ = ui
    page.route('**/api/predict', lambda route: route.abort())
    page.locator('#text').fill('Một câu mới.')
    page.locator('#go').click()
    expect(page.locator('#out p')).to_have_class('err')
    expect(page.locator('#go')).to_be_enabled()
    page.unroute('**/api/predict')
    page.locator('#go').click()
    expect(page.locator('#out .res')).to_be_visible()


def test_timeout_and_duplicate_clicks(ui):
    from playwright.sync_api import expect
    page, _, _ = ui
    requests = []
    page.route('**/api/predict', lambda route: requests.append(route))
    page.locator('#text').fill('Phòng học sạch sẽ.')
    page.locator('#go').click()
    expect(page.locator('#go')).to_be_disabled()
    page.evaluate("document.getElementById('go').click()")
    expect(page.locator('#out p')).to_have_class('err', timeout=13000)
    expect(page.locator('#go')).to_be_enabled()
    assert len(requests) == 1
    for route in requests:
        route.abort()


def test_rejects_prototype_names_as_prediction_labels(ui):
    from playwright.sync_api import expect
    page, _, _ = ui
    page.route('**/api/predict', lambda route: route.fulfill(json={'sentiment':'constructor','topic':'toString','contract_version':'1.0'}))
    page.locator('#text').fill('Một câu mới.')
    page.locator('#go').click()
    expect(page.locator('#out p')).to_have_class('err')
    expect(page.locator('#out .res')).to_have_count(0)


def test_timeout_includes_response_body(ui):
    page, _, _ = ui
    result = page.evaluate("""async () => {
      const original = window.fetch;
      window.fetch = async (path, options) => ({ok:true, status:200, json: () => new Promise((resolve, reject) => {
        options.signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')));
        setTimeout(() => resolve({late:true}), 11000);
      })});
      try { await request('/slow-body'); return 'completed'; }
      catch (error) { return error.kind; }
      finally { window.fetch = original; }
    }""")
    assert result == 'timeout'
