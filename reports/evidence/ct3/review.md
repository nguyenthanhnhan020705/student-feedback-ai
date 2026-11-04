# Independent CT3 review — 2026-10-31

Reviewer: fresh-context ct3_review agent, read-only. Reviewed new runner/tests,
design/plan/ledger and final numerical report against original CT1/CT2 interfaces.
No Critical or Important findings. Full-suite was pending at review time;
subsequently completed 281 passed, 0 skipped, 14 known warnings (197.07s).

Confirmed train-only word/character fits and independent vocabulary/IDF replay;
global ranking with controls; proper percentage-point/relative/joint comparisons;
early existing/live output refusal; source/runtime/control and payload checks.
Final report's numerical claims agree with run-1. No model serving change.

## Deferred minor

reports/ct3_word_char.py verify_experiment does not validate the descriptive
receipt.schema_version or receipt.promotion fields. Reviewer confirmed with an
in-memory-only read probe: unexpected-schema / deployed still verify when all
bound models/metrics/selection/payloads match. Actual results/config/selection and
serving-model preservation remain checked; verified is local replay consistency,
not a certification of every receipt field or external authenticity. No file
was altered by review. Deferred as minor under the execution workflow.

## Declined to judge / disposition

- Deployment readiness: no serving change authorized by the CT1 research protocol;
  research model readiness is checked, production promotion remains separate.
- Independent generalization/statistical significance: no independent new data;
  report only observed validation deltas and known-case diagnostics.
- Malicious local artifacts: only trusted team-local joblib is in scope; hash
  consistency is not a safe-deserialization or signed-authenticity guarantee.
- Work outside CT3: unrelated dirty member work, historical Backend minor, CT4–5,
  Phase 6 and Git/publication stay preserved and outside this review.

Root disposition: accept these boundaries; retain local worktree and ledger,
no commit/push/merge/cleanup/publication. Whole-project completion is not claimed.
