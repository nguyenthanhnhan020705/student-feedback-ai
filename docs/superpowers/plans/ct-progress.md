# SDD ledger — plan: docs/superpowers/plans/2026-10-31-ct1-evaluation.md

Scope: user authorized CT1 only. CT2–CT5 and Phase 6 not started.

Ruling: reuse linked feature/integration-p0 worktree and existing locked venv; preserve dirty member work, no commit/push/merge/cleanup — avoids capturing unrelated work; delivery remains local.
Ruling: execute CT1 directly from the user's approved outline and explicit implementation request — no repeat approval of the same scope; details are documented for review.
Ruling: use persistent ledger and native Python/PowerShell tools instead of Bash skill helpers — Windows environment; helper-specific automation not certified.
Ruling: known-case labels are assistant-proposed and ambiguous expectations are null — no human label review supplied; diagnostic rates cannot establish independent quality.
Pre-flight: Task 1 consumes protocol/cases from Task 2; create those inputs before the real baseline run; metric tests remain independent.

Task 1: complete — RED missing module; GREEN 11 evaluation tests; independent review alignment regression RED 2 tests then GREEN; final combined suite 38 passed, 0 skipped with TV2_RUN_REAL_DATA=1. New tool only, no production behavior changes.
Task 2: complete — protocol, 39 provisional labeled cases, 49-file snapshot and real validation baseline, exact replay against original metrics and per-row predictions. Evidence: reports/evidence/ct1/README.md.
Ruling: preserve first candidate snapshot and create final baseline-v2 after review fix — avoids overwriting audit history; consumers must use v2.
Ruling: no fabricated blind holdout/human review — independent final data remains a later collection step; CT1 establishes the protocol, not independent quality certification.
Final: no deferred minor findings; Important alignment issue resolved and replayed. Model artifacts/metadata match pre-CT1 diagnosis hashes; all application code unchanged.
CT1 complete within documented scope; CT2, CT3, CT4, CT5 and Phase 6 not started. No commit/push/merge or publication.

## CT2 update — 2026-10-31

The CT1-only statements above are historical. User subsequently requested CT2.
CT2 weighting experiments and review are recorded separately in
`ct2-progress.md`; report: `docs/quality/ct2-report.md`. Official final run is
`.local-tools/ct2-class-weights/run-2/`; run-1 remains review history. Serving
models and all CT1 protected inputs are preserved. CT3–CT5/Phase 6 not started.
CT2 complete: 261 tests passed without skips; fresh replay and independent
review issue resolution recorded in `ct2-progress.md`. No automatic promotion.

## CT3 update — 2026-10-31

User confirmed word + character direction. CT3 completed offline experiments:
see ct3-progress.md and docs/quality/ct3-report.md. Twelve fits, fresh replay,
281 tests passed without skips. Sentiment Macro F1 improves; joint Accuracy
declines. Serving baseline preserved. CT4–CT5 and Phase 6 not started.
