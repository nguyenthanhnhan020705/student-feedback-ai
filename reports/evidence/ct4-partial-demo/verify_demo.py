"""Finite no-fit verification of actual CT4 independent-task demo behavior."""
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC


def forbidden(*args,**kwargs):
    raise AssertionError('Demo verification must not fit')


Pipeline.fit=Pipeline.fit_transform=FeatureUnion.fit=FeatureUnion.fit_transform=forbidden
TfidfVectorizer.fit=TfidfVectorizer.fit_transform=LinearSVC.fit=forbidden

from fastapi.testclient import TestClient
from demo_v2.main import create_app
from demo_v2.service import DemoService
from demo_v2.policy import make_prediction
from ml.data import load_split
from reports.ct_evaluation import read,digest
from reports.ct5_selective_prediction import extract_signals,apply_policy,summarize


def main():
    out=Path(__file__).resolve().parent
    service=DemoService(ROOT)
    assert service.ready
    samples=['Tốt','🙂🙂🙂','Thay giang bai de hieu va rat nhiet tinh.',
        'Thầy giảng bài rõ ràng và phòng học thì nóng.',
        'Bài giảng không khó hiểu như em nghĩ.','Quán phở đầu ngõ rất ngon.']
    with TestClient(create_app(service)) as client:
        examples=[]
        for text in samples:
            response=client.post('/api/v2/predict',json={'text':text})
            assert response.status_code==200
            assert response.json()==service.predict(text)
            examples.append(dict(text=text,response=response.json(),label_status='diagnostic_not_independent_truth'))
    frame=load_split(ROOT/'data/raw','validation')
    records=frame.to_dict('records')
    signals={task:extract_signals(pipe,frame.text.tolist(),task) for task,pipe in service.models.items()}
    threshold_map={'zero_plus_margin_q10':service.thresholds}
    decisions=apply_policy(records,signals,'zero_plus_margin_q10',threshold_map)
    for i,d in enumerate(decisions):
        value=make_prediction({t:signals[t][i] for t in signals},service.thresholds)
        for task in signals:
            assert (value[task]['status']=='answered')==d['accepted'][task]
            assert value[task]['label']==(d['raw_prediction'][task] if d['accepted'][task] else None)
    partition=read(ROOT/'.local-tools/ct5-selective-prediction/run-1/partition.json')
    summaries={'full_validation':summarize(decisions)}
    for subset in ('threshold_development','policy_audit'):
        selected=[i for i,r in enumerate(partition['rows']) if r['subset']==subset]
        summaries[subset]=summarize([decisions[i] for i in selected])
    previous=read(ROOT/'.local-tools/ct5-selective-prediction/run-1/metrics.json')['ct4']
    for subset in ('threshold_development','policy_audit'):
        expected=previous[subset]['zero_plus_margin_q10']
        assert summaries[subset]['joint']==expected['joint']
        assert summaries[subset]['tasks']==expected['tasks']
    report=dict(status='local_demo_verified_independent_evaluation_pending',fit=False,
        model='ct4_research_selected',policy='q10_independent_tasks_provisional_demo',
        thresholds=service.thresholds,model_hashes=service.model_hashes,
        ct5_receipt_sha256=digest(ROOT/'.local-tools/ct5-selective-prediction/run-1/receipt.json'),
        source_hashes={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'demo_v2').rglob('*')
                       if p.is_file() and '__pycache__' not in p.parts},
        samples=examples,metrics=summaries,
        full_status_counts=dict(Counter(make_prediction({t:signals[t][i] for t in signals},service.thresholds)['status']
                                       for i in range(len(records)))),
        independent_evaluation='pending_human_reviewed_final_and_answerability',
        limitations=['negation_not_improved','multiple_aspects_not_split','margin_not_probability',
                     'not_an_OOD_detector','known_inputs_observed_before_demo_trial_policy_choice'])
    (out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(verified=True,fit=False,rows=len(records),status_counts=report['full_status_counts'])))


if __name__=='__main__':main()
