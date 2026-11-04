# Independent review — CT4 independent-task trial demo

Fresh read-only reviewer ct4_demo_review inspected only the new demo scope,
tests, source bindings and recorded metrics. No files/index/branch changed;
no expensive suite/replay rerun or classifier fitting by reviewer.

## Initial verdict: changes required

No Critical finding. One Important readiness issue: receipt/config/parent JSON
could be a valid non-object (null/list/number/string) and .get would raise an
uncaught AttributeError; huge integer threshold could raise OverflowError.
Module-level service initialization could crash rather than expose health=false,
503 for valid input and422 for invalid input. Reviewer reproduced these cases.

One UI issue initially graded Minor: editing text while/after prediction leaves
labels associated with an old input. Parent regraded this to Important for this
interactive accuracy demo: shown results must correspond to visible input.

## One parent fix pass, tests first

- review-red.txt: **17 failed,4 passed,63 deselected**, expected .get/overflow
  errors and stale-label browser assertions on both Chrome/Edge.
- Typed JSON object loader for all provenance roots and safe finite numeric
  validation now reject invalid configuration without crashing. Guard is also
  used by independent task policy; no old research runner changed.
- Input edits clear results; pending responses/errors are displayed only if
  current text still matches submitted text. Duplicate-submit/body-timeout
  behavior remains tested.
- review-green.txt: **84 passed**,1 existing warning,66.25s, all new API/browser
  tests. No-fit verification rerun against corrected source; same1583 decisions
  and saved CT5 task/joint metrics. Final whole-suite result is recorded below
  when the process exits; no second independent review claimed.

## Independently confirmed before fix

All eight initial demo source hashes, actual CT4 model hashes, CT4/CT5 receipt
bindings and saved development/audit per-task/joint metrics matched.
1583 rows =1293 complete +267 partial +23 insufficient.
Task null/status coherence, canonical labels, complete-vector/char-only behavior,
finite scores, body deadline, duplicate submit and safe message rendering checked.
No further blocking source finding identified.

## Declined to certify

- Running full regression/replay,654-file preservation, final documentation and
  live port8001: parent runs and records actual checks, not reviewer assumptions.
- Semantic/answerability quality, independent final/OOD performance or production
  suitability of q10: no independent human-reviewed final data exists.
- Negation and multiple-aspect reasoning: explicitly outside user-selected scope.

The final parent audit/ledger resolves engineering completion conditions.
Original v1/CT1–CT5 remain unchanged. q10 is a provisional local trial only.

## Parent closure

Final full suite exited0:435 passed,0 skipped,14 existing warnings in430.55s. Post-suite finalize verifies654/654 preserved original hashes. CT5 fresh no-fit replay and pip check exited0. Corrected-source no-fit verifier retains the same1583 status counts/task/joint metrics. Actual trial HTTP health and partial prediction verified at8001.
Both identified issues resolved in one test-first fix pass; no remaining blocking finding identified in parent completion audit. No second independent review or independent quality certification claimed. New documentation and live evidence are hash-bound in handoff-verification.json.
