"""Bounded CSV parsing independent of model availability."""

import csv
import io

from fastapi import HTTPException, UploadFile
from pydantic import ValidationError

from backend.schemas import PredictRequest

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_ROWS = 1000


def read_texts(file: UploadFile) -> list[str]:
    try:
        if not (file.filename or '').lower().endswith('.csv'):
            raise HTTPException(422, 'Vui lòng chọn tệp .csv UTF-8.')
        content = file.file.read(MAX_FILE_BYTES + 1)
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(413, 'Tệp vượt giới hạn 2 MB (2.097.152 byte).')
        try:
            decoded = content.decode('utf-8-sig')
        except UnicodeDecodeError as exc:
            raise HTTPException(422, 'CSV phải dùng encoding UTF-8.') from exc
        try:
            reader = csv.reader(io.StringIO(decoded, newline=''), strict=True)
            header = next(reader, [])
            if ('text' not in header or len(header) != len(set(header))
                    or any(not name.strip() for name in header)):
                raise HTTPException(422, 'CSV cần header có cột text, không trùng hoặc trống tên cột.')
            text_column = header.index('text')
            texts = []
            for row in reader:
                if not row:
                    continue
                if len(texts) >= MAX_ROWS:
                    raise HTTPException(422, 'CSV chỉ hỗ trợ tối đa 1.000 dòng dữ liệu.')
                if len(row) != len(header):
                    raise HTTPException(422, f'Record {len(texts) + 1} không khớp số cột CSV.')
                try:
                    texts.append(PredictRequest(text=row[text_column]).text)
                except ValidationError as exc:
                    raise HTTPException(422, f'Record {len(texts) + 1}: text phải có nội dung và tối đa 5.000 ký tự.') from exc
            if not texts:
                raise HTTPException(422, 'CSV chưa có dòng dữ liệu.')
            return texts
        except csv.Error as exc:
            raise HTTPException(422, 'CSV sai định dạng hoặc có ô quá dài.') from exc
    finally:
        file.file.close()
