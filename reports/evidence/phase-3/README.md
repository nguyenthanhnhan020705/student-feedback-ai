# Phase 3 — Backend verification

Workspace: `.local-tools/integration-p0`, branch `feature/integration-p0`.
Scope: Backend contract 1.0; no training, artifact changes, UI fixes or Git publication.

## Changes

- Invalid UTF-8 JSON now returns 422 / INVALID_INPUT / `$body/invalid_json`.
  Only the wrapped UnicodeDecodeError on POST `/api/predict` is translated;
  ordinary HTTP errors and headers retain framework behavior.
- Metadata requires a full Python 3.13 version and canonical label order.
  Pipeline classes are still compared as sets, as the contract requires.
- Validation metrics check all required fields, ordered per-class scores,
  matrix dimensions, nonnegative integer counts, support and total alignment.
  Boolean counts, NaN and invalid nested types are rejected.
- Integration checks cover missing artifact/metadata and corrupt artifacts
  for each task, preserving health availability and preventing partial results.

## Reproduce from this workspace

```powershell
./.local-tools/phase1-verify/Scripts/python.exe -m pytest tests/test_backend.py tests/test_health.py tests/test_model_service.py tests/test_predict.py tests/integration/test_prediction_flow.py -q -p no:cacheprovider
./.local-tools/phase1-verify/Scripts/python.exe reports/verify_phase3.py
./.local-tools/phase1-verify/Scripts/python.exe -m pip check
$env:TV2_RUN_REAL_DATA='1'
./.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
```

The locked Phase 1 environment verifies Backend. The existing `.venv` also
has the browser dependencies for the full suite; ML package versions are
unchanged. Full-suite browser tests intentionally refresh the existing real
prediction screenshots/JSON; these do not certify Phase 4.

## Evidence

- `baseline.txt`: 5 failed, 146 passed; UTF-8 and two known UI defects on each
  browser. Collected before edits; pytest may display newer source lines when
  reporting a failure after a file edit. The failing assertions are unchanged.
- `red.txt`: 39 failed, 30 passed before fixes, covering metadata and UTF-8.
- `utf8-red.txt`: three invalid-byte variants fail; three routing controls pass.
- `backend-final.txt`: 119 passed, 1 existing Starlette/httpx deprecation warning.
- `http-verification.json` and server logs: live Uvicorn from external cwd,
  real/missing models, four authored sentences compared to direct pipelines,
  static assets, model-file nonexposure, 405 and invalid-input cases.
- `http-verification.txt`: all 59 Phase 2 protected file hashes unchanged.
- `pip-check.txt`: no broken requirements.
- `full-suite.txt`: 196 passed, 4 failed, 12 existing warnings, no skips;
  includes real Data/ML and Chrome/Edge. Failures are
  `test_rejects_prototype_names_as_prediction_labels` and
  `test_timeout_includes_response_body`, each on both browsers. Known Phase 4
  failures are reported, not excluded or counted as passing.
- `review.md`: independent review, no Critical/Important findings; one deferred
  minor detail-field issue for a malformed Unicode object key.

## Limits

Full product acceptance remains Phase 5. The UI prototype-label and response-body
timeout defects remain Phase 4. The review's malformed-key detail-field minor
is safely rejected with 422 but is not claimed fully contract compliant.
Metadata schema validation does not establish semantic authenticity of every
declared hyperparameter. Artifacts remain trusted local inputs; no distribution
rights or new model-quality claims are made.
