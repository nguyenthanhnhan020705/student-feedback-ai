"""Student Feedback API 3.0: build with create_app(Settings); run with `feedback-ai serve`."""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, ConfigDict, StrictStr, field_validator, model_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

from feedback_ai.services.analysis import AnalysisService
from feedback_ai.config import Settings
from feedback_ai.api.routes.batch import router as batch_router

FRONTEND = Path(__file__).resolve().parent.parent/'web'


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: StrictStr

    @field_validator('text')
    @classmethod
    def valid_text(cls, text):
        if len(text)>5000 or not text.strip():
            raise ValueError('Input must contain 1 to 5000 raw Unicode codepoints')
        try:
            text.encode('utf-8')
        except UnicodeEncodeError as exc:
            raise ValueError('Invalid Unicode') from exc
        return text


class PredictResponse(BaseModel):
    model_config = ConfigDict(extra='forbid',strict=True)
    contract_version: Literal['3.0']
    sentiment: Literal['positive','negative','mixed','undetermined']
    topic: Literal['lecturer','curriculum','facility','education_quality','other_domain']
    topics: list[Literal['lecturer','curriculum','facility']] | None = None

    @model_validator(mode='after')
    def valid_topics(self):
        if self.topic == 'education_quality':
            if not self.topics or len(self.topics) < 2 or len(set(self.topics)) != len(self.topics):
                raise ValueError('Multiple topics require distinct detected topics')
        elif self.topics is not None:
            raise ValueError('Unexpected topic list')
        return self


def error(status,code,message):
    return JSONResponse(status_code=status,content=dict(contract_version='3.0',error=dict(code=code,message=message)))


def create_app(settings: Settings, service=None):
    app=FastAPI(title='Student Feedback AI — CT4 evidence trial',version='3.0.0')
    app.state.service=service if service is not None else AnalysisService(settings.artifacts_dir / "serving")
    app.include_router(batch_router)

    @app.exception_handler(RequestValidationError)
    async def invalid(request:Request,exc:RequestValidationError):
        return error(422,'INVALID_INPUT','Nội dung không hợp lệ. Hãy nhập 1 đến 5000 ký tự Unicode.')

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request:Request,exc:StarletteHTTPException):
        if request.url.path=='/api/v3/predict' and exc.status_code==400 and isinstance(exc.__cause__,UnicodeDecodeError):
            return error(422,'INVALID_INPUT','JSON không hợp lệ.')
        return await http_exception_handler(request,exc)

    @app.exception_handler(Exception)
    async def internal(request:Request,exc:Exception):
        return error(500,'INTERNAL_ERROR','Đã xảy ra lỗi nội bộ.')

    @app.get('/api/health')
    def health():
        current=app.state.service
        return dict(status='ok',ready=current.ready,models=current.status,model='ct4',contract_version='3.0')

    @app.post('/api/v3/predict',response_model=PredictResponse,response_model_exclude_none=True)
    def predict(body:PredictRequest):
        current=app.state.service
        if not current.ready:
            return error(503,'MODEL_NOT_READY','Mô hình CT4 hoặc cấu hình thử nghiệm chưa sẵn sàng.')
        try:
            return PredictResponse.model_validate(current.predict(body.text))
        except Exception:
            return error(500,'INFERENCE_ERROR','Không thể thực hiện phân tích. Bạn vui lòng thử lại.')

    @app.get('/',include_in_schema=False)
    def index():
        return FileResponse(FRONTEND/'index.html')

    @app.get('/{asset}',include_in_schema=False)
    def assets(asset:str):
        if asset == 'mau-phan-hoi.xlsx':
            return FileResponse(FRONTEND/asset,filename=asset)
        if asset not in {'api.js','app.js','styles.css','batch.js','batch.css'}:
            raise HTTPException(404)
        return FileResponse(FRONTEND/asset)

    return app


