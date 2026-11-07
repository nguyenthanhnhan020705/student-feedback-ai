import pytest
from playwright.sync_api import sync_playwright

pytestmark = pytest.mark.browser
CHANNELS = ('chrome', 'msedge')


@pytest.fixture(scope='session')
def playwright_driver():
    with sync_playwright() as driver:
        yield driver


@pytest.fixture(scope='session', params=CHANNELS)
def browser(playwright_driver, request):
    try:
        instance = playwright_driver.chromium.launch(channel=request.param, headless=True)
    except Exception as exc:  # an unavailable required channel is a failure, not a pass
        pytest.fail(f'{request.param} not launchable: {exc}')
    yield instance
    instance.close()


@pytest.fixture
def page(browser, server_url):
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = context.new_page(); page.set_default_timeout(10000)
    errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    assert page.goto(server_url).status == 200
    yield page
    assert errors == [], errors
    context.close()
