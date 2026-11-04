"""Final lightweight audit; no fitting, scoring, control writes or suite rerun."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT/'.local-tools/ct5-selective-prediction/run-1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    receipt = read(RUN/'receipt.json')
    actual = {p.relative_to(RUN).as_posix(): sha(p) for p in RUN.rglob('*')
              if p.is_file() and p != RUN/'receipt.json'}
    assert actual == receipt['payload']
    for name, expected in receipt['source_hashes'].items():
        assert sha(ROOT/name) == expected, name
    inventory = read(OUT/'preexisting.json')
    assert len(inventory) == 603
    assert all((ROOT/n).is_file() and sha(ROOT/n) == expected for n, expected in inventory.items())
    assert sha(RUN/'receipt.json') == sha(OUT/'receipt.json')
    data = (OUT/'full-suite.txt').read_bytes()
    suite = data.decode('utf-16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8')
    assert '351 passed, 14 warnings' in suite and 'skipped' not in suite
    assert read(RUN/'data-status.json')['recommended_policy'] is None
    new = ['reports/ct5_selective_prediction.py', 'tests/test_ct5_selective_prediction.py',
        'docs/quality/ct5-report.md', 'docs/quality/ct5-data-requirements.md',
        'docs/superpowers/plans/2026-11-01-ct5-selective-prediction.md',
        'docs/superpowers/plans/ct5-progress.md']
    report = dict(schema_version='ct5-handoff.1',
        status='engineering_complete_independent_evaluation_pending', promotion='not_deployed',
        recommended_policy=None, run_receipt_sha256=sha(RUN/'receipt.json'),
        verified_run_payloads=len(actual), preserved_preexisting=len(inventory),
        source_and_docs={name: sha(ROOT/name) for name in new},
        evidence={p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob('*')
                  if p.is_file() and p != OUT/'handoff-verification.json'},
        full_suite='351 passed, 0 skipped, 14 known warnings',
        review='no Critical/Important; one deferred defensive Minor')
    (OUT/'handoff-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('source_and_docs','evidence')},indent=2))


if __name__ == '__main__': main()
