"""Write-once core snapshot before the parent's finite exploratory evaluation."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
output=Path(__file__).with_name('core-freeze.json')
if output.exists():
    raise SystemExit('Refusing to overwrite core freeze')
paths=sorted([*ROOT.glob('demo_v3/*.py'),ROOT/'demo_v3/rules.json'])
sources=[ROOT/p for p in ['demo_v2/service.py','demo_v2/policy.py','backend/model_service.py',
    'reports/ct5_selective_prediction.py','reports/ct_evaluation.py',
    '.local-tools/ct4-augmentation/run-1/receipt.json',
    '.local-tools/ct5-selective-prediction/run-1/receipt.json',
    '.local-tools/ct5-selective-prediction/run-1/config.json',
    '.local-tools/ct5-selective-prediction/run-1/thresholds.json']]
sources+=sorted((ROOT/'.local-tools/ct4-augmentation/run-1/research-selected').glob('*'))
def manifest(files):
    return {path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files if path.is_file()}
receipt=dict(schema_version='ct4-v3-core-freeze.1',created_at=datetime.now(timezone.utc).isoformat(),
    status='engineering_complete_independent_evaluation_pending',
    rules_version='experimental-1.0.0',configuration='assistant_authored_specification_exposed',
    core_sha256=manifest(paths),reused_source_sha256=manifest(sources),
    ct4_role='audit_only_does_not_modify_evidence',
    evaluation='Future finite variants are assistant_proposed exploratory checks, not independent validation; no tuning after this freeze.')
output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(receipt=str(output),core_files=len(paths),reused_files=len(sources))))
