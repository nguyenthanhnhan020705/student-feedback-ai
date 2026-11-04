"""Record scoped verification without modifying a frozen source or old evidence."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
directory=Path(__file__).parent
output=directory/'task1-verification.json'
if output.exists():
    raise SystemExit('Refusing to overwrite task1 verification')
freeze=json.loads((directory/'core-freeze.json').read_text(encoding='utf-8'))
for relative,expected in freeze['core_sha256'].items():
    if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()!=expected:
        raise SystemExit('Core changed after freeze: '+relative)
paths=[*ROOT.glob('demo_v3/**/*.py'),ROOT/'demo_v3/rules.json',*ROOT.glob('demo_v3/frontend/*'),
       *ROOT.glob('tests/test_demo_v3*.py'),ROOT/'tests/frontend/test_demo_v3_ui.py']
hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if p.is_file()}
result=dict(schema_version='ct4-v3-task1-verification.1',created_at=datetime.now(timezone.utc).isoformat(),
    source_sha256=hashes,core_unchanged_since_freeze=True,
    scoped_command='./.venv/Scripts/python.exe -B -m pytest tests/test_demo_v3.py tests/test_demo_v3_api.py tests/frontend/test_demo_v3_ui.py -q --tb=short -o cache_dir=reports/evidence/ct4-multilabel/cache-task1',
    passed=173,warnings=1,exit_code=0,seconds=56.84,engine_api_tests=131,browser_tests=42,
    browsers=['chrome','msedge'],actual_cases_each_browser=6,
    warning='Existing StarletteDeprecationWarning about httpx/TestClient; no dependencies changed.',
    evidence='task1-green.txt',core_freeze='core-freeze.json',
    final_integration_review_and_full_suite='owned by parent; not claimed by this task report',
    status='engineering_complete_independent_evaluation_pending')
output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(source_files=len(hashes),core_unchanged=True,verification=str(output))))
