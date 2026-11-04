# SDD ledger — plan: docs/superpowers/plans/2026-10-31-ct2-class-weights.md

Scope: user requested CT2. No automatic serving-model replacement, CT3–CT5 or Phase 6.

Ruling: execute existing CT2 handoff directly and record finite weight choices — explicit implementation request follows prior scope explanation — comparison is limited to three choices, not exhaustive tuning.
Ruling: reuse linked feature/integration-p0, locked venv and persistent native Windows ledger; no commit/cleanup — preserves unrelated dirty work — delivery remains local.
Pre-flight: Task 2 consumes Task 1 weighting/ranking/comparison; existing CT1 evaluator is unchanged. Both tasks share canonical labels and validation-only evaluation.
Baseline: CT1 replay verified 49 inputs, 1583 validation rows, 39 known cases; CT1 tests 13 passed.

- [x] Task 1: tested weighting/fitting/ranking/regressions.
- [x] Task 2: experiment/replay/full verification/review/report.

Task 1: complete — RED missing CT2 module; GREEN 27 passed (14 CT2 + 13 CT1), 2 existing SciPy iprint warnings from fixture LR training. Evidence: red-task1.txt, green-task1.txt.
Task 2: RED 9 expected missing lifecycle API failures, 14 passed; GREEN 36 passed (23 CT2 + 13 CT1), same 2 fixture warnings. Real tiny-data lifecycle has no test directory and verifies research artifacts, preserved inputs and tamper rejection.
Real run-1: 6 fits, no training warnings; validation rank leaders balanced/sqrt_balanced. Fresh-process verify passed. Macro F1 improves but Accuracy/joint accuracy and some known cases regress; retain serving baseline, not an automatic promotion.
Independent ct2_review: no Critical/Minor; Important pairwise tie-chain drift reproduced. Regression test review-red.txt fails (balanced instead of sqrt_balanced). Root cause: moving reference allowed repeated near-ties beyond 1e-6 of maximum F1.
Final: fixed tie-chain ranking — use fixed global F1 band then fixed Accuracy band, baseline/fixed order last. Historical run-1 and its runner copy preserved; final run-2 will bind fixed source. Actual rank leaders are far outside tolerance ties.
Final fix verification: review-green.txt 37 passed (24 CT2 + 13 CT1). Run-2 completed six fits; replay-2.txt passed in a fresh process. All candidate evaluations and combined metrics/regressions match run-1 exactly (run-comparison.txt). No second reviewer is claimed.
Final review scope decisions: unrelated dirty work remains outside CT2; promotion stays deferred; independent generalization/human label review remain unavailable; checksum replay establishes local consistency rather than external authenticity. These preserve the pre-existing scope and its limits rather than create new acceptance gates.

Task 2: complete — final full suite with TV2_RUN_REAL_DATA=1: 261 passed, 0 skipped, 14 known library warnings in 155.59s. Evidence full-suite-final.txt. Fresh final CT1 replay verifies all 49 protected inputs and original metrics/predictions; pip check passed; scoped whitespace checks passed. Both final candidate pairs and combined selection reload under metadata contract 1.0. All six final real fits have no warnings.
Final: fixed Important tie-chain issue — test_selection_does_not_chain_ties_below_global_best_macro_f1 RED→GREEN, final suite 261/261. No Critical/Minor findings remain from scoped review; no re-review claimed.
Final disposition: keep feature/integration-p0 and local uncommitted work as-is per scoped handoff. Do not offer merge/cleanup of the shared member integration workspace. CT2 complete; CT3–CT5/Phase 6 not started, no serving-model replacement/commit/push/merge/publication.
