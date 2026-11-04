"""Verify the newly launched HTTP trial, browser versions and actual results."""
from pathlib import Path
import hashlib
import json
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:8002'
sys.path.insert(0, str(ROOT))


def main():
    from playwright.sync_api import sync_playwright, expect
    with urllib.request.urlopen(BASE+'/api/health', timeout=10) as response:
        health = json.load(response)
    assert health['ready'] and health['contract_version'] == '3.0'
    assets = {}
    for name in ('', 'api.js', 'app.js', 'styles.css'):
        with urllib.request.urlopen(BASE+'/'+name, timeout=10) as response:
            assert response.status == 200
            assets[name or 'index.html'] = hashlib.sha256(response.read()).hexdigest()
    # Samples already exposed by the handoff; these are actual smoke results.
    samples = ['Thầy giảng bài rõ ràng và phòng học thì nóng.',
               'Môn học có ba tín chỉ.', 'Tốt.', '🙂🙂🙂']
    outputs = []
    for text in samples:
        request = urllib.request.Request(BASE+'/api/v3/predict',
            data=json.dumps({'text':text}).encode('utf-8'),
            headers={'Content-Type':'application/json'}, method='POST')
        with urllib.request.urlopen(request, timeout=10) as response:
            outputs.append(dict(text=text, response=json.load(response), fixture=False))
    review_samples = []
    for text, sentiment, topic in (
        ('"Giảng viên tốt\nphòng học nóng" là câu ví dụ.','undetermined','other_domain'),
        ('Giảng viên viết cụm từ tốt và phòng học nóng trên bảng.','undetermined','lecturer'),
        ('Giảng viên từ trường khác đến và dạy tốt.','positive','lecturer'),
        ('Từ tốt và tệ xuất hiện trên trang.','undetermined','other_domain'),
    ):
        request = urllib.request.Request(BASE+'/api/v3/predict',
            data=json.dumps({'text':text}).encode('utf-8'),
            headers={'Content-Type':'application/json'}, method='POST')
        with urllib.request.urlopen(request, timeout=10) as response:
            actual=json.load(response)
        assert actual==dict(contract_version='3.0',sentiment=sentiment,topic=topic)
        review_samples.append(dict(text=text,response=actual,fixture=False,scope='review_regression_smoke'))
    browser_reports = []
    folder = OUT/'live-browser'
    folder.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        for channel in ('chrome', 'msedge'):
            browser = playwright.chromium.launch(channel=channel, headless=True)
            context = browser.new_context(viewport={'width':1280,'height':900})
            page = context.new_page()
            assert page.goto(BASE).status == 200
            expect(page.locator('#go')).to_be_disabled()
            page.locator('#text').fill(samples[0])
            expect(page.locator('#go')).to_be_enabled()
            with page.expect_response('**/api/v3/predict') as pending:
                page.locator('#go').click()
            actual = pending.value.json()
            assert actual == outputs[0]['response']
            expect(page.locator('#out .res b')).to_have_text(['Trung tính','Chất lượng giáo dục'])
            page.screenshot(path=str(folder/f'{channel}-mixed.png'), full_page=True)
            page.locator('#text').fill(samples[1])
            page.locator('#go').click()
            expect(page.locator('#out .res b')).to_have_text(['Chưa xác định','Chương trình đào tạo'])
            page.screenshot(path=str(folder/f'{channel}-information.png'), full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            page.screenshot(path=str(folder/f'{channel}-mobile.png'), full_page=True)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            browser_reports.append(dict(channel=channel, version=browser.version, fixture=False))
            context.close()
            browser.close()
    report = dict(url=BASE, health=health, assets=assets, samples=outputs,review_samples=review_samples,
                  browsers=browser_reports, scope='local_smoke_not_independent_quality_evaluation')
    (OUT/'live-demo.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
