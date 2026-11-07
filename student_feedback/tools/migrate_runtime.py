"""One-time migration. Explicit source argument, never needed at runtime."""
import argparse
import ast
from pathlib import Path
import shutil

def migrate(source, target):
    def put(name,text):
        p=target/'src'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
    def read(name): return (source/name).read_text(encoding='utf-8')
    def function(file,name):
        text=read(file);node=next(n for n in ast.parse(text).body if getattr(n,'name',None)==name)
        return ast.get_source_segment(text,node)+'\n'
    put('feedback_ai/data/preprocessing.py',read('ml/preprocessing.py'))
    put('feedback_ai/common/labels.py',read('ml/labels.py'))
    put('ml/preprocessing.py','"""Compatibility for trusted historical model pickles."""\nfrom feedback_ai.data.preprocessing import normalize_text\n')
    put('feedback_ai/data/transforms.py','import unicodedata\n'+function('reports/ct4_augmentation.py','unaccent'))
    put('reports/ct4_augmentation.py','"""Compatibility for trusted historical model pickles."""\nfrom feedback_ai.data.transforms import unaccent\n')
    put('feedback_ai/inference/signals.py','import numpy as np\nfrom scipy import sparse\nfrom sklearn.pipeline import Pipeline, FeatureUnion\nfrom feedback_ai.inference.policy import LABELS\n'+function('reports/ct5_selective_prediction.py','_nnz')+function('reports/ct5_selective_prediction.py','extract_signals'))
    put('feedback_ai/inference/policy.py',read('demo_v2/policy.py').replace('from ml.labels','from feedback_ai.common.labels'))
    loader=read('backend/model_service.py').replace('from backend.config import MODEL_DIR','MODEL_DIR = None').replace('from ml.labels','from feedback_ai.common.labels')
    loader=loader.replace('model_service = ModelService()','').replace('model_dir: str | Path = MODEL_DIR','model_dir: str | Path')
    put('feedback_ai/inference/model_loader.py',loader)
    put('feedback_ai/common/json_io.py','import json\nfrom pathlib import Path\n'+function('reports/ct_evaluation.py','read')+function('reports/ct_evaluation.py','write_new_json'))
    frozen=read('demo_v2/service.py').replace('from backend.model_service','from feedback_ai.inference.model_loader').replace('from reports.ct_evaluation import read, digest','from feedback_ai.common.json_io import read\nfrom feedback_ai.common.hashing import digest').replace('from reports.ct5_selective_prediction','from feedback_ai.inference.signals').replace('from demo_v2.policy','from feedback_ai.inference.policy')
    frozen=frozen.replace("ROOT = Path(__file__).resolve().parents[1]",'').replace('root=ROOT','root').replace("self.root/'.local-tools/ct4-augmentation/run-1'","self.root/'ct4'").replace("self.root/'.local-tools/ct5-selective-prediction/run-1'","self.root/'ct5'")
    frozen=frozen.replace('class DemoService:','class FrozenModels:')
    frozen=frozen.replace('        try:\n            ct4',"        try:\n            from feedback_ai.inference.bundle import verify_manifest\n            verify_manifest(self.root/'manifest.json')\n            ct4",1)
    put('feedback_ai/inference/frozen.py',frozen)
    detector=read('demo_v3/detector.py').replace('from demo_v3.ontology','from feedback_ai.inference.ontology').replace("Path(__file__).with_name('rules.json')","Path(__file__).resolve().parent.parent/'resources/rules.json'")
    put('feedback_ai/inference/detector.py',detector)
    put('feedback_ai/inference/ontology.py',read('demo_v3/ontology.py'))
    (target/'src/feedback_ai/resources/rules.json').write_bytes((source/'demo_v3/rules.json').read_bytes())
    service=read('demo_v3/service.py').replace('from demo_v2.service import DemoService, ROOT','from feedback_ai.inference.frozen import FrozenModels').replace('from demo_v3.detector','from feedback_ai.inference.detector').replace('from demo_v3.ontology','from feedback_ai.inference.ontology').replace('class Service:','class AnalysisService:').replace('root=ROOT','root').replace('DemoService(Path(root))','FrozenModels(Path(root))')
    put('feedback_ai/services/analysis.py',service)
    imports='import csv\nimport re\nfrom io import BytesIO, StringIO\nfrom zipfile import ZipFile\nfrom pathlib import Path\nfrom collections import Counter\nfrom openpyxl import Workbook, load_workbook\nfrom openpyxl.styles import Font, Alignment\n'
    constants="TOPICS = {'lecturer':'Giảng viên','curriculum':'Chương trình đào tạo','facility':'Cơ sở vật chất'}\nSENTIMENTS = {'positive':'Tích cực','negative':'Tiêu cực','mixed':'Hỗn hợp','undetermined':'Chưa xác định'}\nMAX_BYTES = 5*1024*1024\n"
    put('feedback_ai/common/display.py',constants)
    put('feedback_ai/io/imports.py',imports+'from feedback_ai.common.display import MAX_BYTES\n'+function('demo_v3/batch.py','parse_upload'))
    put('feedback_ai/io/exports.py',imports+'from feedback_ai.common.display import TOPICS, SENTIMENTS\n'+function('demo_v3/batch.py','workbook'))
    put('feedback_ai/services/aspects.py','from feedback_ai.common.display import TOPICS\n'+function('demo_v3/batch.py','aspects'))
    put('feedback_ai/api/batch_schemas.py','from pydantic import BaseModel, ConfigDict, Field, StrictStr\nfrom typing import Literal\n'+function('demo_v3/batch.py','Row')+function('demo_v3/batch.py','ExportRequest'))
    routes=read('demo_v3/batch.py').split("router=APIRouter",1)[1]
    put('feedback_ai/api/routes/batch.py','from fastapi import APIRouter, Request, HTTPException\nfrom fastapi.responses import Response\nfrom starlette.concurrency import run_in_threadpool\nfrom feedback_ai.io.imports import parse_upload\nfrom feedback_ai.io.exports import workbook\nfrom feedback_ai.services.aspects import aspects\nfrom feedback_ai.common.display import MAX_BYTES\nfrom feedback_ai.api.batch_schemas import ExportRequest\nrouter=APIRouter'+routes)
    app=read('demo_v3/main.py').replace('from demo_v3.service import Service','from feedback_ai.services.analysis import AnalysisService\nfrom feedback_ai.config import Settings').replace('from demo_v3.batch','from feedback_ai.api.routes.batch')
    app=app.replace("Path(__file__).with_name('frontend')","Path(__file__).resolve().parent.parent/'web'").replace('def create_app(service=None):','def create_app(settings: Settings, service=None):').replace('else Service()','else AnalysisService(settings.artifacts_dir / "serving")').replace('\napp=create_app()','')
    put('feedback_ai/api/app.py',app)
    for f in (source/'demo_v3/frontend').iterdir():
        if f.is_file():shutil.copy2(f,target/'src/feedback_ai/web'/f.name)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--target',type=Path,required=True)
    a=p.parse_args();migrate(a.source.resolve(),a.target.resolve())
