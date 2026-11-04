# CT4 independent-task demo evidence — 2026-11-01

Scope explicitly authorized by user: trial CT4 on local demo, decide sentiment
and topic independently; defer negation and multi-aspect processing. No training,
Phase6, commits/pushes/merges or publication. New app is demo_v2 on8001; old v1
backend/frontend/model artifacts and frozen CT1–CT5 are preserved.

## Evidence sequence

- red-api.txt: expected missing demo_v2 module.
- green-api.txt:34 passed,1 deselected (static deferred until UI),1 existing warning.
- red-browser.txt: expected HTTP500 because frontend files were not yet created.
- green-demo.txt:63 new API/browser tests passed on Chrome/Edge,39.10s.
- review.md: one fresh-context independent review; Important malformed provenance
  startup crash and stale-text result association (parent regraded to Important).
- review-red.txt:17 failed/4 passed, expected readiness/overflow/stale-label failures.
- review-green.txt:84 passed,1 existing warning,66.25s after one fix pass.
- verification.json/txt: fresh no-fit actual model/service/API checks,1583 validation
  rows,1293 complete267 partial23 insufficient; task/pair metrics match frozen CT5.
- full-suite.txt: initial414-test suite started before review corrections; historical
  evidence only, superseded for final-state claims by **full-suite-final.txt**.
- frozen-ct5-replay.txt: unchanged CT1–CT5 chain replay with fit APIs forbidden.
- pip-check.txt: existing locked environment check.
- preservation.json: original654 byte hashes; baseline refreshes stored separately,
  restored only if differing from verified backup. Finalize again after final suite.
- browser/: actual CT4 UI/API results and screenshots, Chrome/Edge. No mock fallback.
- live-demo.json: actual HTTP health/assets/samples on8001 once final checked.

Final completion and hashes are in handoff-verification.json, written only after
all closing checks. Do not infer success from a file/script merely existing.

## Reproduce

From integration-p0:

```powershell
./.venv/Scripts/python.exe -B -m uvicorn demo_v2.main:app --host 127.0.0.1 --port 8001
./.venv/Scripts/python.exe -B -m pytest tests/test_demo_v2.py tests/frontend/test_demo_v2_ui.py -q -p no:cacheprovider
./.venv/Scripts/python.exe -B reports/evidence/ct4-partial-demo/verify_demo.py
./.venv/Scripts/python.exe -B reports/evidence/ct5/no_fit.py verify
```

Run verify_demo.py only when intentionally refreshing this new demo's evidence.
Never rewrite previous CT1–CT5 receipts or inventories to bypass checks.
q10 is provisional for this user-requested trial; known cases have been observed.
Margin is not probability and low margin does not certify semantic insufficiency.
No independent human-reviewed final/answerability data, no production/OOD claim.
The displayed neutral/other labels retain canonical meanings; withheld labels
are null/status insufficient_information, not neutral/other defaults.
