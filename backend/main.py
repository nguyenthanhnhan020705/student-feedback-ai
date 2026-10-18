"""Run: python -m uvicorn backend.main:app --reload (from repository root)."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.csv_service import read_texts
from backend.metrics_service import read_report
from backend.model_service import ModelService, ModelUnavailable, ROOT
from backend.schemas import (BatchResponse, ERROR_RESPONSES, HealthResponse,
                             MetricsResponse, PredictRequest, PredictResponse)
from ml.labels import LABELS


def get_service(request: Request) -> ModelService:
    return request.app.state.model_service


Service = Annotated[ModelService, Depends(get_service)]


def create_app(service: ModelService | None = None, reports_dir: Path | None = None) -> FastAPI:
    model_service = service if service is not None else ModelService()
    report_root = reports_dir if reports_dir is not None else ROOT / 'reports'

    @asynccontextmanager
    async def lifespan(application):
        model_service.load()
        yield

    application = FastAPI(title='Student Feedback AI', version='0.1.0', lifespan=lifespan)
    application.state.model_service = model_service
    application.mount('/static', StaticFiles(directory=ROOT / 'frontend'), name='static')

    @application.get('/', include_in_schema=False)
    def index():
        return FileResponse(ROOT / 'frontend' / 'index.html')

    @application.get('/api/health', response_model=HealthResponse)
    def health(models: Service):
        loaded = models.models_loaded
        return {'status': 'ready' if all(loaded.values()) else 'setup_required', 'models_loaded': loaded}

    @application.post('/api/predict', response_model=PredictResponse, responses=ERROR_RESPONSES)
    def predict(payload: PredictRequest, models: Service):
        try:
            return models.predict([payload.text])[0]
        except ModelUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc

    @application.post('/api/predict-batch', response_model=BatchResponse,
                      responses={**ERROR_RESPONSES, 413: {'description': 'Tệp vượt 2 MB.'}})
    def predict_batch(file: Annotated[UploadFile, File()], models: Service):
        texts = read_texts(file)
        try:
            predictions = models.predict(texts)
        except ModelUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc
        summary = {task: {label: 0 for label, _ in mapping.values()} for task, mapping in LABELS.items()}
        results = []
        for prediction in predictions:
            row = {'text': prediction['text']}
            for task in LABELS:
                label = prediction[task]['label']
                row[task] = label
                summary[task][label] += 1
            results.append(row)
        return {'total': len(results), 'results': results, 'summary': summary}

    @application.get('/api/metrics', response_model=MetricsResponse)
    def metrics():
        reports = {task: read_report(report_root / f'metrics_{task}.json') for task in LABELS}
        return {'available': all(report['available'] for report in reports.values()), **reports}

    return application


app = create_app()
