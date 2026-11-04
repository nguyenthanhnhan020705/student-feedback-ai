"""Final source/evidence binding; refuses missing acceptance evidence."""
from pathlib import Path
import hashlib
import json
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def log(path):
    raw = path.read_bytes()
    return raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')


def main():
    suite = log(OUT/'full-suite-final.txt')
    result = re.search(r'(\d+) passed, (\d+) warnings in ([^\r\n]+)', suite)
    if not result or re.search(r'\d+ (failed|error|skipped)', suite):
        raise ValueError('Final full suite must pass without failures/errors/skips')
    if 'No broken requirements found.' not in log(OUT/'pip-check.txt'):
        raise ValueError('pip check evidence missing')
    inventory = read(OUT/'preexisting.json')
    changed = [n for n,h in inventory.items() if not (ROOT/n).is_file() or digest(ROOT/n)!=h]
    if changed:
        raise ValueError('Original bytes changed: '+repr(changed))
    history = read(OUT/'historical-replay.json')
    if len(history)!=5 or any(r['exit_code']!=0 or r['fit'] is not False for r in history):
        raise ValueError('Five successful no-fit historical replays required')
    evaluation = read(OUT/'evaluation-final.json')
    for name, expected in read(OUT/'final-suite-source-before.json').items():
        if digest(ROOT/name) != expected:
            raise ValueError('Source changed since stable final suite: '+name)
    for name, expected in evaluation['source_hashes'].items():
        if digest(ROOT/name) != expected:
            raise ValueError('Final evaluation source changed: '+name)
    if evaluation['groups']['specification']['metrics']['joint_exact_match']['correct'] != 15:
        raise ValueError('Specification cases no longer match')
    with urllib.request.urlopen('http://127.0.0.1:8002/api/health',timeout=5) as response:
        health=json.load(response)
    if not health['ready'] or health['contract_version']!='3.0':
        raise ValueError('Live v3 not ready')
    live=read(OUT/'live-demo.json')
    if {r['channel'] for r in live['browsers']} != {'chrome','msedge'}:
        raise ValueError('Live Chrome/Edge evidence required')
    if len(live.get('review_samples',[])) != 4:
        raise ValueError('Final live R1–R4 smoke results required')
    for name in ('api.js','app.js','styles.css','index.html'):
        if digest(ROOT/'demo_v3/frontend'/name)!=live['assets'][name]:
            raise ValueError('Live frontend evidence mismatch')
    if any(not (OUT/name).is_file() for name in (
            'review.md','review-fix-rereview.md','review-r4-verification.json')):
        raise ValueError('Review, scoped re-review and R4 regression closure required')
    source=[p for p in (ROOT/'demo_v3').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    source += list((ROOT/'tests').glob('test_demo_v3*.py'))+[ROOT/'tests/frontend/test_demo_v3_ui.py',
        ROOT/'docs/quality/ct4-multilabel-demo.md',
        ROOT/'docs/superpowers/specs/2026-11-01-ct4-multilabel-design.md',
        ROOT/'docs/superpowers/plans/2026-11-01-ct4-multilabel.md',
        ROOT/'docs/superpowers/plans/ct4-multilabel-progress.md']
    receipt=dict(schema_version='ct4-multilabel-handoff.1',
        status='engineering_complete_independent_evaluation_pending',url=live['url'],
        full_suite=result.group(0),skipped=0,preserved_originals=len(inventory),
        historical_fit=False,detector='experimental_contextual_rules_CT4_audit_only',
        ontology='3.0',independent_human_reviewed_evaluation='pending',
        quality_errors=evaluation['groups']['exploratory']['quality_errors'],
        review_closure='independent_R1_R3_rereview_then_R4_test_first_correction_no_further_independent_review',
        source_and_docs={p.relative_to(ROOT).as_posix():digest(p) for p in source},
        evidence={p.relative_to(OUT).as_posix():digest(p) for p in OUT.rglob('*')
                  if p.is_file() and p.name!='handoff-verification.json' and 'cache-task1' not in p.parts
                  and p.suffix not in ('.log','.pid')})
    (OUT/'handoff-verification.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_and_docs','evidence')},indent=2))


if __name__=='__main__':
    main()
