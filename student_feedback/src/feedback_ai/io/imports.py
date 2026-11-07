import csv
import re
from io import BytesIO, StringIO
from zipfile import ZipFile
from pathlib import Path
from collections import Counter
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment
from feedback_ai.common.display import MAX_BYTES
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
