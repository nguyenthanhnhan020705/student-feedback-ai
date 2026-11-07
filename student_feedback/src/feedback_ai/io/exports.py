import csv
import re
from io import BytesIO, StringIO
from zipfile import ZipFile
from pathlib import Path
from collections import Counter
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment
from feedback_ai.common.display import TOPICS, SENTIMENTS
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
