from io import BytesIO
import pytest

def test_csv_preserves_duplicates_blank_and_multiline():
    from demo_v3.batch import parse_upload
    result = parse_upload('a.csv', 'text,id\n"First.\nSecond.",a\nSame,b\nSame,c\n,d\n'.encode())
    assert result['sheets'][0]['rows'] == [['First.\nSecond.','a'],['Same','b'],['Same','c'],['','d']]

def test_aspects_do_not_spread_polarity_between_topics():
    from demo_v3.batch import aspects
    clauses=[dict(topics=['lecturer'],positive=True,negative=False),dict(topics=['facility'],positive=False,negative=True)]
    assert aspects(clauses)=={'lecturer':'positive','facility':'negative'}
    assert aspects([dict(topics=['lecturer','facility'],positive=True,negative=True)])=={'lecturer':'undetermined','facility':'undetermined'}

def test_export_preserves_text_as_text():
    from demo_v3.batch import workbook
    from openpyxl import load_workbook
    row=dict(id='PH001',source_row=2,text='=1+1',status='ok',sentiment='positive',topics=['lecturer'],aspects={'lecturer':'positive'},error='')
    book=load_workbook(BytesIO(workbook('Example',[row])))
    assert book.sheetnames==['Tổng quan','Chi tiết','Theo chủ đề']
    assert book['Chi tiết']['C2'].value=='=1+1'
    assert book['Chi tiết']['C2'].data_type=='s'

def test_import_limits():
    from demo_v3.batch import parse_upload
    with pytest.raises(ValueError): parse_upload('a.csv', ('text\n'+'a\n'*501).encode())

def test_excel_import_and_api_export():
    from openpyxl import Workbook, load_workbook
    from demo_v3.batch import parse_upload
    book=Workbook();book.active.append(['id','feedback']);book.active.append(['a','One.\nTwo.'])
    stream=BytesIO();book.save(stream)
    result=parse_upload('a.xlsx',stream.getvalue())
    assert result['sheets'][0]['rows']==[['a','One.\nTwo.']]

def test_live_analysis_aspects_and_limits():
    from demo_v3.main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        assert client.get('/api/health').json()['ready']
        response=client.post('/api/v3/analyze-row',json={'text':'Giảng viên nhiệt tình nhưng phòng học nóng.'})
        assert response.status_code==200
        assert response.json()['aspects']=={'lecturer':'positive','facility':'negative'}
        for text in ['', ' '*5, 'a'*5001]:
            assert client.post('/api/v3/analyze-row',json={'text':text}).status_code==422
        assert client.post('/api/v3/import?filename=a.csv',content=b'text\na\na\n').json()['sheets'][0]['rows']==[['a'],['a']]

def test_export_control_characters_and_leading_excel_rows():
    from demo_v3.batch import parse_upload, workbook
    from openpyxl import Workbook, load_workbook
    row=dict(id='a',source_row=1,text='hello\x0bworld',status='invalid',sentiment=None,topics=[],aspects={},error='')
    book=load_workbook(BytesIO(workbook('name',[row])))
    assert book['Chi tiết']['C2'].value=='hello\\u000bworld'
    source=Workbook();source.active.append([]);source.active.append([]);source.active.append([])
    source.active.append(['text'])
    for _ in range(500): source.active.append(['hello'])
    stream=BytesIO();source.save(stream)
    result=parse_upload('input.xlsx',stream.getvalue())
    assert len(result['sheets'][0]['rows'])==500
    assert result['sheets'][0]['first_row']==5

def test_summary_counts_multi_topics_with_success_denominator():
    from demo_v3.batch import workbook, parse_upload
    from openpyxl import load_workbook
    rows=[dict(id='1',source_row=1,text='a',status='ok',sentiment='mixed',topics=['lecturer','facility'],aspects={'lecturer':'positive','facility':'negative'},error=''),
          dict(id='2',source_row=2,text='',status='invalid',sentiment=None,topics=[],aspects={},error='blank')]
    sheet=load_workbook(BytesIO(workbook('test',rows)))['Tổng quan']
    values={r[0]:r[1:] for r in sheet.iter_rows(values_only=True)}
    assert values['Thành công'][0]==1
    assert values['Giảng viên']==(1,1)
    assert values['Cơ sở vật chất']==(1,1)
    assert len(parse_upload('a.csv',('text\n'+'same\n'*500).encode())['sheets'][0]['rows'])==500
