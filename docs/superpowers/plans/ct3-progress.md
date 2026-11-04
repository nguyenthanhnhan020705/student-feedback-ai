# SDD ledger — plan: docs/superpowers/plans/2026-10-31-ct3-word-char.md

Scope: implement CT3 word + character direction confirmed by user; quantify
improvement over original and CT2. No automatic serving replacement.

Ruling: execute directly within user's approved direction; finite feature weights
and char range are documented implementation choices — no repeat approval needed;
the comparison only covers these choices, not all possible representations.
Ruling: reuse existing linked integration worktree, locked venv and native ledger;
preserve dirty work, no commit/cleanup/push/merge — local delivery only.
Pre-flight: Task 2 consumes Task 1 build/rank/percent helpers; both consume frozen
CT1 evaluator and CT2 comparison/verification; interfaces are compatible.
Ruling: report validation development improvement only; independent final data is
absent — cannot certify accuracy on arbitrary new feedback.

Task 1: complete — RED missing CT3 module; GREEN 46 tests (CT1/CT2/CT3),
2 existing SciPy iprint fixture warnings. green-task1.txt.
Task 2 RED: 11 expected missing lifecycle API failures, 9 passed.
Lifecycle GREEN investigation: vectorizer get_params includes numpy.float64 type
under dtype, not JSON serializable; serialize its explicit dtype name. This
changes only metadata serialization, not model features or fitting.

Task 2 lifecycle GREEN: 57 tests passed (20 CT3, 13 CT1, 24 CT2), 2 existing
SciPy warnings; real fixture has no test split and replay forbids LinearSVC.fit.
Real run-1 started after these tests; six fixed variants, twelve train-only fits.
Full real-data/browser suite running; production app and serving models unchanged.

Task 2: complete — run-1 twelve train-only fits without warnings; fresh-process
replay passed 12 artifacts plus selection, train vocab/IDF, metadata and full
metrics/deltas/percentages. CT1 49 live inputs and CT2 19 payloads unchanged.
Full suite TV2_RUN_REAL_DATA=1: 281 passed, 0 skipped, 14 known library warnings,
197.07s; pip check passed. No production behavior changes.

Independent ct3_review: no Critical/Important; checked numerical report against
actual run-1 evidence. Final: minor (deferred): receipt.schema_version and
receipt.promotion are descriptive and not checked during replay; actual
models/payload/selection remain checked. See reports/evidence/ct3/review.md.

Final: Ruling: deployment readiness is outside this offline experiment — keep
serving baseline despite Macro F1 gain; research readiness is verified — users
do not receive new predictions until a separate promotion decision.
Final: Ruling: generalization/significance remain unestablished — report observed
validation and provisional-case deltas only — small measured changes cannot be
claimed as reliable new-feedback accuracy improvements.
Final: Ruling: trusted team-local artifacts only — hashes demonstrate replay
consistency, not safe untrusted joblib loading or authenticated provenance.
Final: Ruling: preserve unrelated dirty work/historical Backend minor/Phase 6 and
CT4–5 — no commit/push/merge/publication or workspace cleanup — local handoff only.

Result: sentiment Macro F1 75.2966% -> 78.9855%, but Accuracy declines. Global
selection retains CT2 topic. Joint 1296 -> 1291/1583 (-0.3159 pp); CT3-only pair
1286/1583 (-0.6317 pp). No overall accuracy improvement claim. CT3 complete;
all artifacts/ledger/worktree retained, no automatic deployment.
