# Phase 4 — Frontend (2026-10-31)

Workspace: `.local-tools/integration-p0`, branch `feature/integration-p0`.
Scope: approved Phase 4 only, API contract 1.0 unchanged. No training,
artifact changes, commit, push, merge or Phase 5–6 delivery work.

## Changes and reproduction

- `frontend/api.js`: prediction labels must be strings and own properties of
  the canonical label maps. Inherited names and array-to-string coercion are rejected.
- AbortController's 10000 ms deadline remains active while reading JSON.
  AbortError becomes timeout; transport failures become network errors.
  Malformed JSON retains HTTP error mapping (422/503/500); malformed successful
  predictions are rejected, never replaced with sample labels.
- Existing UI finally releases loading, retains input and permits retry.
  No framework or feature added; desktop layout retained after visual inspection.
- Tests add independent bad-label cases, body timeout through the UI and real
  retry, malformed response statuses, health reconnect and mobile MOCK visibility.

From the integration workspace, using the existing browser-enabled environment:

```powershell
./.venv/Scripts/python.exe -m pytest tests/frontend/test_ui.py -q -p no:cacheprovider
$env:TV2_RUN_REAL_DATA='1'
./.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
```

## Evidence

- `api-before.js`, `test_ui-before.py`: snapshots before this phase, because HEAD
  still contains the historical scaffold and does not isolate this phase's diff.
- `red.txt`: original tests, 4 expected failures across Chrome/Edge. Source-line
  excerpts may reflect test edits made while pytest was running; collected test
  identities and assertions are the original four cases.
- `expanded-red.txt`: expanded Chrome tests before production edits, 6 failed,
  5 passed. Unknown label and malformed JSON controls already passed.
- `browser-green.txt`: complete frontend run after fixes (see final summary).
- `full-suite.txt`: full-suite result after fixes (see final summary).
- `../frontend/{chrome,msedge}-real-prediction.{json,png}`: current actual model
  response, browser version and screenshot. No fixture in this real inference test.
- `{chrome,msedge}-mobile-mock.png`: explicitly labeled development fixtures,
  not evidence of model predictions. Viewport 390 × 844; desktop 1280 × 900.
- `protected-hashes-before.txt`: all 59 Phase 2 protected inputs match.

## Final verification

- Frontend: **42 passed**, 103.60 seconds; Chrome 147.0.7727.101 and
  Edge 156.0.4314.50, no skips/warnings.
- Full suite with `TV2_RUN_REAL_DATA=1`: **224 passed**, 154.50 seconds,
  no skips, 12 existing warnings (Starlette/httpx deprecation and SciPy `iprint`).
- `pip check`: no broken requirements. Scoped code/document diff check passed.
- All 59 protected Data/ML hashes match before and after; no artifact retraining.
- Independent fresh-context review found no Critical/Important/Minor issues in
  the Phase 4 changes; see `review.md`. Its pending full-suite condition is now
  satisfied by `full-suite.txt`.
- Desktop real inference and mobile MOCK screenshots inspected on both browsers;
  layout retained, with no horizontal overflow at the tested mobile viewport.

## Remaining scope

Phase 5 still owns whole-product acceptance, restart/offline rehearsal and demo
packaging; Phase 6 owns final report/slides. Passing a suite does not complete
those tasks. Phase 3's existing malformed Unicode key detail-field minor remains
documented there. Dataset rights and model quality claims are unchanged.
