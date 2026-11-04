"""Record the R4 correction without replacing prior revision evidence."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
directory=Path(__file__).parent
output=directory/'review-r4-verification.json'
if output.exists():
    raise SystemExit('Refusing to overwrite R4 verification')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
previous=json.loads((directory/'review-fix-verification.json').read_text(encoding='utf-8'))
freeze=json.loads((directory/'core-freeze.json').read_text(encoding='utf-8'))
raw_log=(directory/'review-r4-green.txt').read_bytes()
log=raw_log.decode('utf-16' if raw_log.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8')
match=re.search(r'(\d+) passed, (\d+) warning in ([\d.]+)s',log)
if not match or int(match[1])!=167:
    raise SystemExit('Missing complete scoped engine/API GREEN167 result')
diff=[]
for relative,snapshot in [('demo_v3/detector.py','detector-before-r4.py.txt'),
                          ('tests/test_demo_v3.py','test-demo-v3-before-r4.py.txt')]:
    if sha(directory/snapshot)!=previous['source_sha256'][relative]:
        raise SystemExit('R4 snapshot differs from previous revision: '+relative)
    diff.extend(difflib.unified_diff((directory/snapshot).read_text(encoding='utf-8').splitlines(keepends=True),
        (ROOT/relative).read_text(encoding='utf-8').splitlines(keepends=True),
        fromfile='review-fix/'+relative,tofile='review-r4/'+relative))
(directory/'review-r4.diff').write_text(''.join(diff),encoding='utf-8')
hashes={relative:sha(ROOT/relative) for relative in previous['source_sha256']}
changed=[relative for relative,value in hashes.items() if value!=previous['source_sha256'][relative]]
if changed!=['demo_v3/detector.py','tests/test_demo_v3.py']:
    raise SystemExit('Unexpected changed sources: '+repr(changed))
for relative,expected in freeze['reused_source_sha256'].items():
    if sha(ROOT/relative)!=expected:
        raise SystemExit('Reused frozen source changed: '+relative)
result=dict(schema_version='ct4-v3-review-r4.1',created_at=datetime.now(timezone.utc).isoformat(),
    revision='bounded-context-review-fix.2',source_sha256=hashes,changed_sources=changed,
    previous_revision_receipt='review-fix-verification.json',previous_revision_receipt_sha256=sha(directory/'review-fix-verification.json'),
    original_freeze='core-freeze.json',original_freeze_sha256=sha(directory/'core-freeze.json'),
    original_task1_receipt='task1-verification.json',original_task1_receipt_sha256=sha(directory/'task1-verification.json'),
    rules_unchanged=hashes['demo_v3/rules.json']==freeze['core_sha256']['demo_v3/rules.json'],
    reused_frozen_sources_unchanged=True,
    rationale='R4 recognizes explicit sentence-initial word-occurrence/reporting context without restoring every-tu suppression; preserves R1-R3 and ordinary source-preposition evidence.',
    focused_red=dict(log='review-r4-red.txt',failed=6,passed=4,deselected=118,exit_code=1),
    green=dict(log='review-r4-green.txt',passed=int(match[1]),warnings=int(match[2]),seconds=float(match[3]),exit_code=0,
               scope='all v3 engine/API tests'),
    browser='No frontend changes; previous42 Chrome/Edge tests passed in review-green.txt; browser tests not rerun in this R4 scoped command.',
    final_full_suite='Parent will rerun on this final source; earlier full-suite-final runs are superseded.',
    evaluation='Original exploratory evaluation remains historical for original freeze; no exploratory tuning or fresh independent-evaluation claim.',
    status='engineering_complete_independent_evaluation_pending')
output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(receipt=str(output),passed=int(match[1]),changed_sources=changed,rules_unchanged=result['rules_unchanged'])))
