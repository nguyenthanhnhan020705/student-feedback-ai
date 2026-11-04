"""Local, ephemeral feedback import, aspect attribution and Excel reporting."""
import csv
import re
from io import BytesIO, StringIO
from zipfile import ZipFile
from pathlib import Path
from collections import Counter
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Literal

TOPICS = {'lecturer':'Giảng viên','curriculum':'Chương trình đào tạo','facility':'Cơ sở vật chất'}
SENTIMENTS = {'positive':'Tích cực','negative':'Tiêu cực','mixed':'Hỗn hợp','undetermined':'Chưa xác định'}
MAX_BYTES = 5*1024*1024

def aspects(clauses):
    found = {t for c in clauses for t in c['topics']}
    result = {}
    for topic in TOPICS:
        if topic not in found: continue
        certain = [c for c in clauses if c['topics']==[topic]]
        positive = any(c['positive'] for c in certain)
        negative = any(c['negative'] for c in certain)
        result[topic] = {(True,True):'mixed',(True,False):'positive',(False,True):'negative',(False,False):'undetermined'}[positive,negative]
    return result

def parse_upload(filename, raw):
    if len(raw)>MAX_BYTES: raise ValueError('File vượt quá 5 MiB.')
    suffix=Path(filename).suffix.lower()
    sheets=[]
    def collect(name, iterator):
        rows=[]; header=None; header_row=0
        for number,values in enumerate(iterator,1):
            values=['' if v is None else str(v) for v in values]
            if len(values)>100 or any(len(v)>20000 for v in values):
                raise ValueError('File có quá nhiều cột hoặc ô quá dài.')
            if header is None:
                if not any(v.strip() for v in values): continue
                header=values;header_row=number;continue
            rows.append(values)
            if len(rows)>500: raise ValueError('Mỗi trang tính tối đa 500 phản hồi.')
        if header is not None:
            width=max([len(header)]+[len(r) for r in rows])
            header += ['']*(width-len(header))
            sheets.append(dict(name=name,headers=[v or f'Cột {i+1}' for i,v in enumerate(header)],rows=[r+['']*(width-len(r)) for r in rows],first_row=header_row+1))
    if suffix=='.csv':
        try: text=raw.decode('utf-8-sig')
        except UnicodeDecodeError: raise ValueError('CSV cần được lưu với mã hóa UTF-8.')
        try: dialect=csv.Sniffer().sniff(text[:8192],delimiters=',;\t')
        except csv.Error: dialect=csv.excel
        collect('CSV',csv.reader(StringIO(text),dialect))
    elif suffix=='.xlsx':
        with ZipFile(BytesIO(raw)) as archive:
            if sum(i.file_size for i in archive.infolist())>25*1024*1024: raise ValueError('File Excel giải nén quá lớn.')
        book=load_workbook(BytesIO(raw),read_only=True,data_only=False,keep_links=False)
        try:
            if len(book.worksheets)>10: raise ValueError('Tối đa 10 trang tính.')
            for sheet in book:
                if sheet.max_row and sheet.max_row>10000: raise ValueError('Trang tính có quá nhiều dòng trống hoặc dữ liệu.')
                collect(sheet.title,sheet.iter_rows(values_only=True))
        finally: book.close()
    else: raise ValueError('Chỉ hỗ trợ CSV và Excel .xlsx.')
    if not sheets: raise ValueError('File không có hàng tiêu đề.')
    return {'sheets':sheets}

class Row(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    id: StrictStr=Field(max_length=100)
    source_row: int=Field(ge=1)
    text: StrictStr=Field(max_length=20000)
    status: Literal['ok','error','invalid','pending']
    sentiment: Literal['positive','negative','mixed','undetermined'] | None=None
    topics: list[Literal['lecturer','curriculum','facility']]=Field(default_factory=list,max_length=3)
    aspects: dict[Literal['lecturer','curriculum','facility'],Literal['positive','negative','mixed','undetermined']]=Field(default_factory=dict)
    error: StrictStr=Field(default='',max_length=500)

class ExportRequest(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    name: StrictStr=Field(default='',max_length=200)
    rows: list[Row]=Field(min_length=1,max_length=500)

def workbook(name, rows):
    def safe(value):
        if isinstance(value,str):
            return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]',lambda m:f'\\u{ord(m[0]):04x}',value)
        return value
    name=safe(name)
    rows=[{**r,**{key:safe(r.get(key,'')) for key in ('id','text','error')}} for r in rows]
    book=Workbook(); summary=book.active;summary.title='Tổng quan'
    good=[r for r in rows if r['status']=='ok']; n=len(good)
    counts=Counter(r['sentiment'] for r in good)
    summary.append(['Đợt phân tích',name]);summary.append(['Tổng phản hồi',len(rows)])
    summary.append(['Thành công',n]);summary.append(['Lỗi / không hợp lệ',sum(r['status'] in ('error','invalid') for r in rows)])
    summary.append(['Chưa phân tích',sum(r['status']=='pending' for r in rows)])
    summary.append(['Nhóm','Số lượng','Tỷ lệ trên phản hồi thành công'])
    for key,label in SENTIMENTS.items(): summary.append([label,counts[key],counts[key]/n if n else 0])
    for key,label in TOPICS.items():
        count=sum(key in r['topics'] for r in good);summary.append([label,count,count/n if n else 0])
    unknown=sum(not r['topics'] for r in good);summary.append(['Chủ đề chưa xác định',unknown,unknown/n if n else 0])
    summary.append(['Lưu ý','Một phản hồi có thể có nhiều chủ đề. Tỷ lệ chủ đề có thể vượt 100%.'])
    summary.append(['Phương pháp','Bộ luật thử nghiệm; model CT4 đối chiếu. Chưa có đánh giá độc lập.'])
    summary.append(['Ký tự đặc biệt','Ký tự không hợp lệ trong XML được biểu diễn bằng mã \\uXXXX trong Excel.'])
    detail=book.create_sheet('Chi tiết');detail.append(['Mã','Dòng nguồn','Nội dung','Trạng thái','Cảm xúc','Chủ đề','Lỗi'])
    aspect=book.create_sheet('Theo chủ đề');aspect.append(['Mã','Dòng nguồn','Chủ đề','Cảm xúc theo chủ đề'])
    for r in rows:
        detail.append([r['id'],r['source_row'],r['text'],r['status'],SENTIMENTS.get(r.get('sentiment'),''),' + '.join(TOPICS[t] for t in r['topics']) or ('Chưa xác định' if r['status']=='ok' else ''),r.get('error','')])
        for t,s in r['aspects'].items(): aspect.append([r['id'],r['source_row'],TOPICS[t],SENTIMENTS[s]])
    for sheet in book:
        sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
        for cell in sheet[1]: cell.font=Font(bold=True)
        for row in sheet:
            for cell in row:
                if isinstance(cell.value,str): cell.data_type='s'
                cell.alignment=Alignment(wrap_text=True,vertical='top')
        for col in sheet.columns: sheet.column_dimensions[col[0].column_letter].width=35
    stream=BytesIO();book.save(stream);book.close();return stream.getvalue()

router=APIRouter(prefix='/api/v3')

@router.post('/import')
async def import_file(request:Request,filename:str):
    raw=bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw)>MAX_BYTES: raise HTTPException(413,'File vượt quá 5 MiB.')
    try: return await run_in_threadpool(parse_upload,filename,bytes(raw))
    except ValueError as exc: raise HTTPException(422,str(exc))
    except Exception: raise HTTPException(422,'Không đọc được file. Kiểm tra CSV/Excel và hàng tiêu đề.')

@router.post('/analyze-row')
def analyze_row(body:dict,request:Request):
    text=body.get('text')
    if not isinstance(text,str) or not text.strip() or len(text)>5000:
        raise HTTPException(422,'Phản hồi cần từ 1 đến 5000 ký tự.')
    try: text.encode('utf-8')
    except UnicodeEncodeError: raise HTTPException(422,'Unicode không hợp lệ.')
    service=request.app.state.service
    if not service.ready: raise HTTPException(503,'Mô hình chưa sẵn sàng.')
    try:
        output,audit=service.analyze(text)
        per_topic=aspects(audit['clauses'])
        return dict(sentiment=output['sentiment'],topics=list(per_topic),aspects=per_topic)
    except Exception: raise HTTPException(500,'Không phân tích được phản hồi này.')

@router.post('/export')
def export(body:ExportRequest):
    data=workbook(body.name,[r.model_dump() for r in body.rows])
    return Response(data,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename="phan-hoi-sinh-vien.xlsx"'})
