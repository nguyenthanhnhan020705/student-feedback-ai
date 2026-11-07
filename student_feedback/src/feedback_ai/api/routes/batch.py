from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from starlette.concurrency import run_in_threadpool
from feedback_ai.io.imports import parse_upload
from feedback_ai.io.exports import workbook
from feedback_ai.services.aspects import aspects
from feedback_ai.common.display import MAX_BYTES
from feedback_ai.api.batch_schemas import ExportRequest
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
