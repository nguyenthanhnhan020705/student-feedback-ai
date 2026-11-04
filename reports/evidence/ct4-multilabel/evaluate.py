"""Finite exploratory checks under ontology 3.0; never an independent benchmark."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def forbid_fit():
    from sklearn.pipeline import Pipeline, FeatureUnion
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import LinearSVC
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    def forbidden(*args, **kwargs):
        raise AssertionError('Exploratory evaluation may not fit or retrain')
    for cls in (Pipeline, FeatureUnion, TfidfVectorizer, LinearSVC, LogisticRegression, MultinomialNB):
        cls.fit = forbidden
        if hasattr(cls, 'fit_transform'):
            cls.fit_transform = forbidden


def hashes():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT/'demo_v3').rglob('*')
            if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}


def specification_cases():
    mapping = {'Tích cực':'positive', 'Tiêu cực':'negative', 'Trung tính':'mixed',
               'Chưa xác định':'undetermined', 'Giảng viên':'lecturer',
               'Chương trình đào tạo':'curriculum', 'Cơ sở vật chất':'facility',
               'Chất lượng giáo dục':'education_quality', 'Lĩnh vực khác':'other_domain'}
    cases = []
    handoff = ROOT/'docs/quality/ct4-multilabel-agent-handoff.md'
    for line in handoff.read_text(encoding='utf-8').splitlines():
        parts = [s.strip().replace('**','') for s in line.strip('|').split('|')]
        if len(parts) == 3 and parts[1] in mapping and parts[2] in mapping and parts[0] != 'Đầu vào':
            cases.append(dict(id=f'spec-{len(cases)+1:03}', text=parts[0],
                              sentiment=mapping[parts[1]], topic=mapping[parts[2]],
                              provenance='user_confirmed_specification_not_holdout'))
    if len(cases) != 15:
        raise ValueError('Specification table parser mismatch')
    return cases


def score(rows):
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    label_sets = {'sentiment':['positive','negative','mixed','undetermined'],
                  'topic':['lecturer','curriculum','facility','education_quality','other_domain']}
    result = {'n_rows':len(rows), 'tasks':{}}
    for task, labels in label_sets.items():
        truth = [r['expected'][task] for r in rows]
        prediction = [r['response'][task] for r in rows]
        result['tasks'][task] = dict(accuracy=float(accuracy_score(truth,prediction)),
            label_order=labels, confusion_matrix=confusion_matrix(truth,prediction,labels=labels).tolist(),
            classification_report=classification_report(truth,prediction,labels=labels,
                                                        output_dict=True,zero_division=0))
    correct = sum(all(r['expected'][task] == r['response'][task] for task in label_sets) for r in rows)
    result['joint_exact_match'] = dict(correct=correct, total=len(rows), ratio=correct/len(rows))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-name', choices=('evaluation.json','evaluation-final.json'),
                        default='evaluation.json')
    args = parser.parse_args()
    forbid_fit()
    before = hashes()
    if not before:
        raise ValueError('No frozen demo sources')
    # The input file is authored only after the detector/config freeze receipt.
    variants = json.loads((OUT/'exploratory-cases.json').read_text(encoding='utf-8'))
    from fastapi.testclient import TestClient
    from demo_v3.main import app
    groups = {'specification':specification_cases(), 'exploratory':variants['cases']}
    outputs = {}
    with TestClient(app) as client:
        health = client.get('/api/health').json()
        if not health['ready']:
            raise ValueError('Trial is not ready')
        for name, cases in groups.items():
            rows = []
            for case in cases:
                response = client.post('/api/v3/predict', json={'text':case['text']})
                if response.status_code != 200:
                    raise RuntimeError(f'{case["id"]}: technical failure {response.status_code}')
                value = response.json()
                if value.get('contract_version') != '3.0':
                    raise ValueError('Wrong contract')
                direct, audit = app.state.service.analyze(case['text'])
                if direct != value:
                    raise ValueError('API/service mismatch')
                expected = {task:case[task] for task in ('sentiment','topic')}
                rows.append(dict(id=case['id'],text=case['text'],provenance=case['provenance'],
                                 expected=expected,response=value,internal_audit=audit,
                                 exact_match=all(value[t]==expected[t] for t in expected)))
            outputs[name] = dict(rows=rows, metrics=score(rows),
                                 quality_errors=[r['id'] for r in rows if not r['exact_match']])
    if hashes() != before:
        raise RuntimeError('Detector/config changed while evaluating')
    report = dict(schema_version='ct4-multilabel-evaluation.1',fit=False,
        status='engineering_complete_independent_evaluation_pending',
        evaluated_at=datetime.now(timezone.utc).isoformat(),source_hashes=before,
        input_sha256=hashlib.sha256((OUT/'exploratory-cases.json').read_bytes()).hexdigest(),
        scope='finite_exploratory_assistant_proposed_not_independent_or_human_reviewed',
        ontology='3.0_not_comparable_to_UIT_VSFC_accuracy',groups=outputs)
    target=OUT/args.output_name
    if target.exists():
        raise ValueError('Refusing to overwrite frozen exploratory evaluation')
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({k:dict(joint=v['metrics']['joint_exact_match'],errors=v['quality_errors'])
                      for k,v in outputs.items()},indent=2))


if __name__ == '__main__':
    main()
