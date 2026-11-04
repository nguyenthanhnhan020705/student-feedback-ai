"""Write-once revision receipt; original freeze/evaluation/receipts stay intact."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
directory=Path(__file__).parent
output=directory/'review-fix-verification.json'
if output.exists():
    raise SystemExit('Refusing to overwrite review-fix verification')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
freeze=json.loads((directory/'core-freeze.json').read_text(encoding='utf-8'))
original=json.loads((directory/'task1-verification.json').read_text(encoding='utf-8'))
raw_log=(directory/'review-green.txt').read_bytes()
log=raw_log.decode('utf-16' if raw_log.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8')
match=re.search(r'(\d+) passed, (\d+) warning in ([\d.]+)s',log)
if not match or int(match[1])!=199:
    raise SystemExit('Missing complete GREEN199 result')
before_detector=(directory/'detector-before-review-fix.py.txt').read_text(encoding='utf-8')
if sha(directory/'detector-before-review-fix.py.txt')!=freeze['core_sha256']['demo_v3/detector.py']:
    raise SystemExit('Before-detector bytes do not match original freeze')
before_test_path=ROOT/'.local-tools/ct4-multilabel-before-review-fix/tests/test_demo_v3.py'
if sha(before_test_path)!=original['source_sha256']['tests/test_demo_v3.py']:
    raise SystemExit('Parent before-test snapshot does not match original receipt')
before_test=before_test_path.read_text(encoding='utf-8')
diff=[]
for relative,before in [('demo_v3/detector.py',before_detector),('tests/test_demo_v3.py',before_test)]:
    after=(ROOT/relative).read_text(encoding='utf-8')
    diff.extend(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),
        fromfile='original-freeze/'+relative,tofile='review-fix/'+relative))
(directory/'review-fix.diff').write_text(''.join(diff),encoding='utf-8')
hashes={relative:sha(ROOT/relative) for relative in original['source_sha256']}
changed=[relative for relative,value in hashes.items() if value!=original['source_sha256'][relative]]
if changed!=['demo_v3/detector.py','tests/test_demo_v3.py']:
    raise SystemExit('Unexpected changed source paths: '+repr(changed))
for relative,expected in freeze['reused_source_sha256'].items():
    if sha(ROOT/relative)!=expected:
        raise SystemExit('Reused source changed: '+relative)
result=dict(schema_version='ct4-v3-review-fix.1',created_at=datetime.now(timezone.utc).isoformat(),
    revision='bounded-context-review-fix.1',old_freeze='core-freeze.json',
    old_freeze_sha256=sha(directory/'core-freeze.json'),old_task1_receipt='task1-verification.json',
    old_task1_receipt_sha256=sha(directory/'task1-verification.json'),
    source_sha256=hashes,changed_sources=changed,rules_unchanged=True,reused_frozen_sources_unchanged=True,
    rationale=['R1: mask supported paired quotations across line breaks while preserving raw offsets',
               'R2: identify bounded metalinguistic complements before contrast/coordinating segmentation and release subsequent independent assertions',
               'R3: distinguish explicit lexical-governor/definition uses of tu from ordinary source prepositions'],
    focused_red=dict(log='review-red.txt',failed=22,passed=4,deselected=92,exit_code=1),
    green=dict(log='review-green.txt',passed=int(match[1]),warnings=int(match[2]),seconds=float(match[3]),exit_code=0,
        engine_api_tests=157,browser_tests=42,browsers=['chrome','msedge']),
    scope='Detector context and regression tests only; no sentiment/topic lexicon expansion, fitting or tuning of exploratory errors.',
    evaluation='Original saved exploratory results apply to original freeze only; this revision has regression verification and no fresh holdout claim.',
    status='engineering_complete_independent_evaluation_pending')
output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(receipt=str(output),changed_sources=changed,passed=int(match[1]),rules_unchanged=True)))
