"""Chrome/Edge v3 acceptance; fixtures explicitly separated from actual output."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

import pytest
from playwright.sync_api import expect
from test_ui import browser_instance

ROOT=Path(__file__).resolve().parents[2]
pytestmark=pytest.mark.browser


@pytest.fixture(scope='module')
def v3_url():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    url=f'http://127.0.0.1:{port}'
    process=subprocess.Popen([sys.executable,'-B','-m','uvicorn','demo_v3.main:app','--host','127.0.0.1','--port',str(port)],
        cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            if process.poll() is not None: pytest.fail('v3 server exited')
            try:
                with urllib.request.urlopen(url+'/api/health',timeout=1) as response:
                    assert json.load(response)['ready'] is True
                break
            except OSError: time.sleep(.1)
        else: pytest.fail('v3 startup deadline')
        yield url
    finally:
        process.terminate();process.wait(timeout=10)


@pytest.fixture
def v3_page(v3_url,browser_instance):
    browser,name=browser_instance
    context=browser.new_context(viewport={'width':1280,'height':900})
    page=context.new_page();page.set_default_timeout(10000)
    assert page.goto(v3_url).status==200
    expect(page.locator('#health')).to_have_text('CT4 v3 sẵn sàng')
    yield page,name
    context.close()


@pytest.mark.parametrize('text,labels,name',[
    ('Thầy giảng bài rõ ràng và phòng học thì nóng.',['Trung tính','Chất lượng giáo dục'],'mixed-multiple'),
    ('Thầy và cô đều giảng dễ hiểu.',['Tích cực','Giảng viên'],'positive-lecturer'),
    ('Chương trình có quá nhiều lý thuyết.',['Tiêu cực','Chương trình đào tạo'],'negative-curriculum'),
    ('Phòng học có máy chiếu.',['Chưa xác định','Cơ sở vật chất'],'information-facility'),
    ('Tốt.',['Tích cực','Lĩnh vực khác'],'positive-unspecified'),
    ('🙂🙂🙂',['Chưa xác định','Lĩnh vực khác'],'no-evidence'),
])
def test_actual_labels(v3_page,browser_instance,text,labels,name):
    page,channel=v3_page
    page.locator('#text').fill(text)
    with page.expect_response('**/api/v3/predict') as received:
        page.locator('#go').click()
    output=received.value.json()
    expect(page.locator('#out .res b')).to_have_text(labels)
    expect(page.locator('#text')).to_have_value(text)
    expect(page.locator('#go')).to_be_enabled()
    directory=ROOT/'reports/evidence/ct4-multilabel/browser';directory.mkdir(parents=True,exist_ok=True)
    page.screenshot(path=str(directory/f'{channel}-{name}.png'),full_page=True)
    (directory/f'{channel}-{name}.json').write_text(json.dumps(dict(browser=channel,
        browser_version=browser_instance[0].version,input=text,response=output,fixture=False),ensure_ascii=False,indent=2),encoding='utf-8')


def valid_result():
    return dict(contract_version='3.0',sentiment='positive',topic='other_domain')


@pytest.mark.parametrize('bad',['constructor','__proto__','array','boxed','version','null','extra','inherited'])
def test_strict_response_validation(v3_page,bad):
    page,_=v3_page
    if bad in ['inherited','boxed']:
        page.evaluate('''kind=>{
            window.fetch=async()=>({ok:true,status:200,json:async()=>kind==='inherited'
                ?Object.create({contract_version:'3.0',sentiment:'positive',topic:'other_domain'})
                :{contract_version:'3.0',sentiment:new String('positive'),topic:'other_domain'}});
        }''',bad)
    else:
        data=valid_result()
        if bad in ['constructor','__proto__']:data['sentiment']=bad
        elif bad=='array':data['sentiment']=['positive']
        elif bad=='version':data['contract_version']='2.0'
        elif bad=='null':data=None
        else:data['audit']={}
        page.route('**/api/v3/predict',lambda route:route.fulfill(json=data))
    page.locator('#text').fill('Một câu thử.')
    page.locator('#go').click()
    expect(page.locator('#out .error')).to_be_visible()
    expect(page.locator('#out .res')).to_have_count(0)
    expect(page.locator('#go')).to_be_enabled()


def test_body_timeout_duplicate_prevention_and_recovery(v3_page):
    page,_=v3_page
    page.evaluate('''()=>{
        window.realFetch=window.fetch;window.callCount=0;
        const originalTimeout=window.setTimeout;
        window.setTimeout=(fn,ms,...args)=>originalTimeout(fn,ms===10000?150:ms,...args);
        window.fetch=async()=>{window.callCount++;return {ok:true,status:200,json:()=>new Promise(()=>{})};};
    }''')
    page.locator('#text').fill('Tốt');page.locator('#go').click()
    page.evaluate("document.getElementById('go').click()")
    expect(page.locator('#out .error')).to_contain_text('10 giây')
    assert page.evaluate('window.callCount')==1
    expect(page.locator('#go')).to_be_enabled()
    page.evaluate('window.fetch=window.realFetch')
    page.locator('#go').click()
    expect(page.locator('#out .res b')).to_have_text(['Tích cực','Lĩnh vực khác'])


@pytest.mark.parametrize('away_back',[False,True])
def test_edit_inflight_invalidates_even_away_then_back(v3_page,away_back):
    page,_=v3_page
    pending=[]
    page.route('**/api/v3/predict',lambda route:pending.append(route))
    page.locator('#text').fill('Tốt');page.locator('#go').click()
    expect(page.locator('#go')).to_be_disabled()
    page.locator('#text').fill('Một câu khác')
    if away_back: page.locator('#text').fill('Tốt')
    assert len(pending)==1
    pending[0].fulfill(json=valid_result())
    expect(page.locator('#go')).to_be_enabled()
    expect(page.locator('#out')).to_be_empty()
    page.unroute('**/api/v3/predict')
    page.locator('#text').fill('Tốt');page.locator('#go').click()
    expect(page.locator('#out .res')).to_be_visible()
    page.locator('#text').fill('Đã đổi câu')
    expect(page.locator('#out')).to_be_empty()


@pytest.mark.parametrize('status',[422,503,500])
def test_errors_clear_labels_keep_input_and_recover(v3_page,status):
    page,_=v3_page
    page.locator('#text').fill('Tốt');page.locator('#go').click()
    expect(page.locator('#out .res')).to_be_visible()
    page.route('**/api/v3/predict',lambda route:route.fulfill(status=status,json={'contract_version':'3.0','error':{'code':'FIXTURE_ERROR'}}))
    page.locator('#go').click()
    expect(page.locator('#out .error')).to_be_visible()
    expect(page.locator('#out .res')).to_have_count(0)
    expect(page.locator('#text')).to_have_value('Tốt')
    if status==503:
        expect(page.locator('#go')).to_be_disabled()
        page.locator('#recheck').click()
    expect(page.locator('#go')).to_be_enabled()


def test_codepoint_count_mobile_and_network_recovery(v3_page):
    page,_=v3_page
    page.locator('#text').fill(' \n\t');expect(page.locator('#go')).to_be_disabled()
    page.locator('#text').fill('🙂'*5000)
    expect(page.locator('#count')).to_have_text('5000 / 5000')
    expect(page.locator('#go')).to_be_enabled()
    page.locator('#text').fill('🙂'*5001);expect(page.locator('#go')).to_be_disabled()
    page.route('**/api/health',lambda route:route.abort())
    page.locator('#recheck').click()
    expect(page.locator('#health')).to_have_text('Không kết nối được máy chủ')
    page.unroute('**/api/health');page.locator('#recheck').click()
    expect(page.locator('#health')).to_have_text('CT4 v3 sẵn sàng')
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#text').fill('Tốt');page.locator('#go').click()
    expect(page.locator('#out .res b')).to_have_text(['Tích cực','Lĩnh vực khác'])
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
