"""Real browser acceptance for the selected local demo (start port 8002 first)."""
from io import BytesIO
import json
from pathlib import Path
from openpyxl import Workbook, load_workbook
from playwright.sync_api import sync_playwright, expect

def test_batch_end_to_end(tmp_path):
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True)
        page=browser.new_page(viewport={'width':1280,'height':900})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8002/')
        page.get_by_role('tab',name='Danh sách phản hồi').click()
        page.locator('#batch-name').fill('Đợt kiểm thử')
        page.locator('#batch-text').fill('Giảng viên nhiệt tình nhưng phòng học nóng.\nGiảng viên nhiệt tình.\nGiảng viên nhiệt tình.\n\n🙂')
        page.locator('#preview-paste').click()
        expect(page.locator('#batch-table tbody tr')).to_have_count(5)
        page.locator('#batch-run').click()
        expect(page.locator('#batch-export')).to_be_enabled(timeout=60000)
        expect(page.locator('#batch-summary')).to_contain_text('Thành công: 4')
        expect(page.locator('#batch-table tbody tr').first).to_contain_text('Hỗn hợp')
        expect(page.locator('#batch-table tbody tr').first).to_contain_text('Giảng viên: Tích cực')
        expect(page.locator('#batch-table tbody tr').first).to_contain_text('Cơ sở vật chất: Tiêu cực')
        page.locator('#topic-filter').select_option('facility')
        expect(page.locator('#batch-table tbody tr')).to_have_count(1)
        with page.expect_download() as download: page.locator('#batch-export').click()
        target=tmp_path/'report.xlsx';download.value.save_as(target)
        book=load_workbook(target);assert book['Chi tiết'].max_row==6
        assert book['Tổng quan']['B1'].value=='Đợt kiểm thử'
        assert book['Theo chủ đề'].max_row==5
        book.close()
        page.get_by_role('tab',name='Nhập file',exact=True).click()
        page.locator('#batch-file').set_input_files({'name':'input.csv','mimeType':'text/csv','buffer':'id,text\na,"Giảng viên nhiệt tình.\nPhòng học nóng."\nb,🙂\n'.encode()})
        expect(page.locator('#file-options')).to_be_visible()
        page.locator('#file-options summary').click()
        page.locator('#column-select').select_option('1');page.locator('#id-select').select_option('0')
        page.locator('#preview-file').click();expect(page.locator('#batch-table tbody tr')).to_have_count(2)
        expect(page.locator('#batch-table tbody tr').first).to_contain_text('Dòng 2')
        page.locator('#batch-run').click();expect(page.locator('#batch-export')).to_be_enabled(timeout=60000)
        book=Workbook();book.active.append(['Nội dung']);book.active.append(['Phòng học sạch sẽ.']);stream=BytesIO();book.save(stream)
        page.locator('#batch-file').set_input_files({'name':'input.xlsx','mimeType':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','buffer':stream.getvalue()})
        expect(page.locator('#batch-table tbody tr')).to_have_count(1)
        page.locator('#batch-run').click();expect(page.locator('#batch-export')).to_be_enabled(timeout=60000)
        expect(page.locator('#batch-table tbody tr')).to_contain_text('Cơ sở vật chất')
        # One failed row must not abort subsequent rows; retry is available.
        page.get_by_role('tab',name='Danh sách phản hồi').click()
        expect(page.locator('#topic-filter')).to_have_value('facility')
        page.locator('#topic-filter').select_option('')
        expect(page.locator('#batch-table tbody tr')).to_have_count(5)
        page.locator('#batch-text').fill('Giảng viên nhiệt tình.\nPhòng học nóng.')
        page.locator('#preview-paste').click()
        calls=[0]
        def fail_first(route):
            calls[0]+=1
            if calls[0]==1: route.fulfill(status=500,content_type='application/json',body='{}')
            else: route.continue_()
        page.route('**/api/v3/analyze-row',fail_first)
        page.locator('#batch-run').click();expect(page.locator('#batch-export')).to_be_enabled(timeout=60000)
        expect(page.locator('#batch-summary')).to_contain_text('Thành công: 1')
        page.unroute('**/api/v3/analyze-row',fail_first)
        page.locator('#batch-run').click();expect(page.locator('#batch-export')).to_be_enabled(timeout=60000)
        expect(page.locator('#batch-summary')).to_contain_text('Thành công: 2')
        assert not errors
        browser.close()
