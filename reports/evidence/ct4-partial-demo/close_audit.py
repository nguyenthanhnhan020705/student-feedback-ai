"""Closing audit of new trial and all retained originals; no fitting/suite rerun."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    data=(OUT/'full-suite-final.txt').read_bytes()
    suite=data.decode('utf-16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8')
    assert '435 passed, 14 warnings' in suite and 'skipped' not in suite
    originals=read(OUT/'preexisting.json')
    assert len(originals)==654 and all((ROOT/n).is_file() and sha(ROOT/n)==h for n,h in originals.items())
    proof=read(OUT/'verification.json')
    for name,h in proof['source_hashes'].items():assert sha(ROOT/name)==h,name
    assert proof['fit'] is False
    for channel in ('chrome','msedge'):
        for kind in ('partial','insufficient','unaccented'):
            r=read(OUT/f'browser/{channel}-{kind}.json')
            assert r['fixture'] is False and r['response']['contract_version']=='2.0'
    base='http://127.0.0.1:8001'
    with urllib.request.urlopen(base+'/api/health',timeout=5) as response:
        health=json.loads(response.read().decode('utf-8'))
    assert health['ready'] and health['model']=='ct4'
    assets={}
    for asset in ('','api.js','app.js','styles.css'):
        with urllib.request.urlopen(base+'/'+asset,timeout=5) as response:
            assert response.status==200
            assets[asset or 'index.html']=hashlib.sha256(response.read()).hexdigest()
    examples=[]
    for text in ('Tốt','🙂🙂🙂','Thay giang bai de hieu va rat nhiet tinh.'):
        request=urllib.request.Request(base+'/api/v2/predict',
            data=json.dumps(dict(text=text)).encode('utf-8'),headers={'Content-Type':'application/json'},method='POST')
        with urllib.request.urlopen(request,timeout=5) as response:
            result=json.loads(response.read().decode('utf-8'))
        expected=next(x['response'] for x in proof['samples'] if x['text']==text)
        assert result==expected
        examples.append(dict(text=text,response=result))
    (OUT/'live-demo.json').write_text(json.dumps(dict(url=base,health=health,assets=assets,samples=examples),ensure_ascii=False,indent=2),encoding='utf-8')
    generated=[*ROOT.joinpath('demo_v2').rglob('*'),ROOT/'tests/test_demo_v2.py',ROOT/'tests/frontend/test_demo_v2_ui.py',
        ROOT/'docs/quality/ct4-partial-demo.md',ROOT/'docs/superpowers/specs/2026-11-01-ct4-partial-demo-design.md',
        ROOT/'docs/superpowers/plans/2026-11-01-ct4-partial-demo.md',ROOT/'docs/superpowers/plans/ct4-partial-demo-progress.md']
    receipt=dict(schema_version='ct4-partial-demo.1',status='local_demo_verified_independent_evaluation_pending',
        url=base,model='ct4',policy='q10_independent_tasks_provisional_trial',fit=False,
        full_suite='435 passed,0 skipped,14 existing warnings',preserved_originals=654,
        source_and_docs={p.relative_to(ROOT).as_posix():sha(p) for p in generated if p.is_file() and '__pycache__' not in p.parts},
        evidence={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p!=OUT/'handoff-verification.json'},
        review='initial readiness and input-association findings fixed RED-to-GREEN; no second independent review',
        ct4_ct5_models_unchanged=True,negation='deferred',production_policy='not_selected')
    (OUT/'handoff-verification.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_and_docs','evidence')},indent=2))


if __name__=='__main__':main()
