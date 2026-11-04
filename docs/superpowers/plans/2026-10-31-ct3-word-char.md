# CT3 Word + Character Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans task-by-task.

**Goal:** Implement and measure word/character candidates against original and CT2.
**Architecture:** Offline runner reuses CT1 evaluate and CT2 comparisons and
verified controls. New combined pipeline; separate local research artifacts.
**Tech Stack:** Existing locked CPython 3.13, scikit-learn, scipy, pytest.
**Spec:** ../specs/2026-10-31-ct3-design.md and docs/quality/ct1-protocol.md.

## Global constraints

Train only; validation selection; no test inference. Six variants / twelve fits.
char_wb (3,5), min_df=2, word:char 1:{0.5,1,2}; weights none/CT2 train-derived.
Preserve serving models, all frozen CT1 inputs and CT2 run-2. No deployment/Git
integration/publication. Reuse linked worktree, persistent ledger and venv.

## Review focus

1. Validation leakage: both vocabularies/IDF must be train-only, inference no fit.
2. Selection: fixed global tie bands, controls included, no known-case ranking.
3. Honest comparison: joint metric, regressions and percentage-point vs relative.
4. Artifact/config/metadata tampering must fail, including receipt consistency.
5. Existing or serving output paths must fail before writing/fitting.

## Task 1 — Pipeline and comparison tests

Files: reports/ct3_word_char.py, tests/test_ct3_word_char.py.
Interfaces: build_candidate(task, train, char_weight, weighting, ct2_selection),
select_candidate(metrics), percentage_change(before, after).

- [x] RED: tests for shared normalizer, feature branches, train-only vocabulary,
  baseline preservation, invalid splits/classes, global ties and percent units.
- [x] GREEN: implement pipeline/ranking/comparison helpers; run CT1/CT2/CT3 tests.

## Task 2 — Experiment, replay and evidence

Interfaces: run_experiment(root, output, ct2_output=None),
verify_experiment(root, output, ct2_output=None); CLI run|verify.
Files: runner/tests above; docs/quality/ct3-report.md, reports/evidence/ct3/,
README.md and docs/superpowers/plans/ct3-progress.md.

- [x] RED: no-test fixture lifecycle, output refusal, tampered payload/control,
  incomplete run and replay without fit; preserve all frozen inputs.
- [x] GREEN: exclusive run paths, fixed config before fit, serialized research
  pipelines/metadata, full metrics/deltas, combined selection and hash receipt.
- [x] Run twelve real fits, replay fresh process, verify CT1/CT2 preservation.
- [x] Run full real-data/browser suite and pip check, record actual warnings.
- [x] Fresh independent review; regressions for Important fixes; report actual
  accuracy/joint/F1 deltas and limitations; keep all work local.

Execution authorized by user's implementation request and direction confirmation;
do not repeat approval for routine implementation. No commit steps in dirty shared
integration; keep ledger and artifacts instead of deleting workspace.
