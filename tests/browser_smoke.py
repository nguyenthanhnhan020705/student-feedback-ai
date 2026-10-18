"""Optional real-browser smoke with missing models; no mocked AI output.

Run with the app already serving:
python tests/browser_smoke.py --url http://127.0.0.1:8765 --executable <browser-path>
"""

import argparse
from pathlib import Path


def main():
    from playwright.sync_api import expect, sync_playwright

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    parser.add_argument('--executable', help='Installed Chrome/Edge executable; otherwise Playwright Chromium')
    args = parser.parse_args()
    output = Path(__file__).resolve().parents[1] / '.local-tests' / 'phase-a'
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=args.executable)
        page = browser.new_page(viewport={'width': 1365, 'height': 950})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        try:
            page.goto(args.url, wait_until='networkidle')
            expect(page.locator('#health')).to_contain_text('Cần thiết lập mô hình')
            page.locator('#feedback').fill('Một phản hồi kiểm tra giao diện')
            page.locator('#single-submit').click()
            expect(page.locator('#single-message')).to_contain_text('Mô hình chưa sẵn sàng')
            expect(page.locator('#sentiment-result')).to_have_text('Chưa có kết quả')

            page.get_by_role('tab', name='Phân tích CSV').click()
            page.locator('#csv-file').set_input_files({
                'name': 'invalid.csv', 'mimeType': 'text/csv', 'buffer': b'wrong\ninput'
            })
            page.locator('#batch-submit').click()
            expect(page.locator('#batch-message')).to_contain_text('cột text')
            page.locator('#csv-file').set_input_files({
                'name': 'valid.csv', 'mimeType': 'text/csv', 'buffer': 'text\nPhản hồi kiểm thử'.encode()
            })
            page.locator('#batch-submit').click()
            expect(page.locator('#batch-message')).to_contain_text('Mô hình chưa sẵn sàng')
            expect(page.locator('#export')).to_be_disabled()
            page.get_by_role('tab', name='Dashboard').click()
            expect(page.locator('#dashboard-empty')).to_be_visible()
            expect(page.locator('#dashboard-content')).to_be_hidden()
            page.get_by_role('tab', name='Đánh giá ML').click()
            expect(page.locator('#metrics-message')).to_contain_text('Chưa có đủ báo cáo')
            expect(page.locator('#metrics-content')).not_to_contain_text('Accuracy:')
            page.get_by_role('tab', name='Đánh giá ML').press('Home')
            expect(page.locator('#single')).to_be_visible()
            page.screenshot(path=str(output / 'desktop.png'), full_page=True)

            page.set_viewport_size({'width': 390, 'height': 844})
            for name in ('Phân tích AI', 'Phân tích CSV', 'Dashboard', 'Đánh giá ML'):
                page.get_by_role('tab', name=name, exact=True).click()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), name
            page.screenshot(path=str(output / 'mobile.png'), full_page=True)
            assert not errors, errors
            print('Browser smoke PASS: 4 tabs, missing-model 503, invalid CSV, empty dashboard/metrics, keyboard, desktop/mobile, no JS exceptions.')
        finally:
            browser.close()


if __name__ == '__main__':
    main()
