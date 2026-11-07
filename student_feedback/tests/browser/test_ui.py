"""Chrome and Edge acceptance against a real server and the real frozen bundle."""
from io import BytesIO

import pytest
from openpyxl import Workbook, load_workbook
from playwright.sync_api import expect

pytestmark = pytest.mark.browser
TABS = ('single', 'paste', 'file')


@pytest.mark.parametrize('text,labels', [
    ('Thầy giảng bài rõ ràng và phòng học thì nóng.', ['Hỗn hợp', 'Giảng viên + Cơ sở vật chất']),
    ('Thầy và cô đều giảng dễ hiểu.', ['Tích cực', 'Giảng viên']),
    ('Chương trình có quá nhiều lý thuyết.', ['Tiêu cực', 'Chương trình đào tạo']),
    ('🙂🙂🙂', ['Chưa xác định', 'Chưa xác định']),
])
def test_single_labels(page, text, labels):
    expect(page.locator('#health')).to_have_text('Đã kết nối')
    page.locator('#text').fill(text)
    page.locator('#go').click()
    expect(page.locator('#out .res b')).to_have_text(labels)
    expect(page.locator('#text')).to_have_value(text)
    expect(page.locator('#go')).to_be_enabled()


def test_health_failure_then_recovery(page):
    page.route('**/api/health', lambda route: route.abort())
    page.reload()
    expect(page.locator('#health')).to_have_text('Mất kết nối')
    expect(page.locator('#recheck')).to_be_visible()
    expect(page.locator('#go')).to_be_disabled()
    page.unroute('**/api/health')
    page.locator('#recheck').click()
    expect(page.locator('#health')).to_have_text('Đã kết nối')
    expect(page.locator('#recheck')).to_be_hidden()


def test_server_error_keeps_input(page):
    page.route('**/api/v3/predict', lambda route: route.fulfill(
        status=500, content_type='application/json',
        body='{"contract_version":"3.0","error":{"code":"INTERNAL_ERROR","message":"x"}}'))
    page.locator('#text').fill('Tốt.')
    page.locator('#go').click()
    expect(page.locator('#out .res')).to_have_count(0)
    expect(page.locator('#text')).to_have_value('Tốt.')
    expect(page.locator('#go')).to_be_enabled()


def test_tabs_keyboard_and_isolation(page):
    page.locator('#tab-paste').click()
    page.locator('#batch-text').fill('Giảng viên nhiệt tình.')
    page.locator('#tab-paste').press('ArrowRight')
    expect(page.locator('#tab-file')).to_have_attribute('aria-selected', 'true')
    page.locator('#tab-file').press('ArrowLeft')
    expect(page.locator('#tab-paste')).to_have_attribute('aria-selected', 'true')
    expect(page.locator('#batch-text')).to_have_value('Giảng viên nhiệt tình.')
    page.locator('#tab-single').click()
    expect(page.locator('#panel-single')).to_be_visible()


def test_paste_batch_filter_export(page, tmp_path):
    page.locator('#tab-paste').click()
    page.locator('#batch-name').fill('Đợt kiểm thử')
    page.locator('#batch-text').fill('Giảng viên nhiệt tình nhưng phòng học nóng.\nGiảng viên nhiệt tình.\nGiảng viên nhiệt tình.\n\n🙂')
    page.locator('#preview-paste').click()
    expect(page.locator('#batch-table tbody tr')).to_have_count(5)
    page.locator('#batch-run').click()
    expect(page.locator('#batch-export')).to_be_enabled(timeout=60000)
    expect(page.locator('#batch-summary')).to_contain_text('Thành công: 4')
    first = page.locator('#batch-table tbody tr').first
    expect(first).to_contain_text('Hỗn hợp')
    expect(first).to_contain_text('Giảng viên: Tích cực')
    expect(first).to_contain_text('Cơ sở vật chất: Tiêu cực')
    page.locator('#topic-filter').select_option('facility')
    expect(page.locator('#batch-table tbody tr')).to_have_count(1)
    with page.expect_download() as download:
        page.locator('#batch-export').click()
    target = tmp_path / 'report.xlsx'
    download.value.save_as(target)
    book = load_workbook(target)
    assert book['Chi tiết'].max_row == 6, 'export must include all rows while filtered'
    assert book['Tổng quan']['B1'].value == 'Đợt kiểm thử'
    book.close()


def test_file_import_csv_and_xlsx(page):
    page.locator('#tab-file').click()
    page.locator('#batch-file').set_input_files({'name': 'input.csv', 'mimeType': 'text/csv',
        'buffer': 'id,text\na,"Giảng viên nhiệt tình.\nPhòng học nóng."\nb,🙂\n'.encode()})
    expect(page.locator('#file-options')).to_be_visible()
    page.locator('#file-options summary').click()
    page.locator('#column-select').select_option('1')
    page.locator('#id-select').select_option('0')
    page.locator('#preview-file').click()
    expect(page.locator('#batch-table tbody tr')).to_have_count(2)
    expect(page.locator('#batch-table tbody tr').first).to_contain_text('Dòng 2')
    page.locator('#batch-run').click()
    expect(page.locator('#batch-export')).to_be_enabled(timeout=60000)
    book = Workbook()
    book.active.append(['Nội dung'])
    book.active.append(['Phòng học sạch sẽ.'])
    stream = BytesIO()
    book.save(stream)
    page.locator('#batch-file').set_input_files({'name': 'input.xlsx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'buffer': stream.getvalue()})
    expect(page.locator('#batch-table tbody tr')).to_have_count(1)
    page.locator('#batch-run').click()
    expect(page.locator('#batch-export')).to_be_enabled(timeout=60000)
    expect(page.locator('#batch-table tbody tr')).to_contain_text('Cơ sở vật chất')


def test_row_failure_continues(page):
    page.locator('#tab-paste').click()
    page.locator('#batch-text').fill('Giảng viên nhiệt tình.\nPhòng học nóng.')
    page.locator('#preview-paste').click()
    calls = [0]

    def fail_first(route):
        calls[0] += 1
        if calls[0] == 1:
            route.fulfill(status=500, content_type='application/json', body='{}')
        else:
            route.continue_()
    page.route('**/api/v3/analyze-row', fail_first)
    page.locator('#batch-run').click()
    expect(page.locator('#batch-export')).to_be_enabled(timeout=60000)
    expect(page.locator('#batch-summary')).to_contain_text('Thành công: 1')


@pytest.mark.parametrize('tab', TABS)
def test_mobile_has_no_horizontal_page_scroll(browser, server_url, tab):
    context = browser.new_context(viewport={'width': 390, 'height': 800}, is_mobile=True)
    page = context.new_page()
    page.set_default_timeout(10000)
    page.goto(server_url)
    page.locator(f'#tab-{tab}').click()
    assert page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth') <= 1
    context.close()
