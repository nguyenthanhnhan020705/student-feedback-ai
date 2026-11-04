# CT4 train-only unaccented augmentation implementation plan

> **For agentic workers:** Use superpowers:executing-plans; execute inline with tests before code. No commits or cleanup in this preserved dirty integration worktree.

**Goal:** Quantify finite train-only augmentation against Original/CT2/CT3 without changing serving models.
**Architecture:** Offline CT4 runner replays frozen controls, clones their pipelines, augments only train, evaluates original validation and separate synthetic stress, serializes research models and verifies all semantics without fitting.
**Tech Stack:** Existing locked Python 3.13, pandas, scikit-learn, pytest and browsers; no new dependencies.
**Spec:** docs/quality/ct4-agent-handoff.md (user selected and authorized this design).

## Global Constraints

- NFC → NFD → remove combining marks → đ/Đ to d/D → NFC; preserve other characters.
- Eligible train rows only; SHA256 ct4-v1|42|<id>, floor 25/50/100%; nested subsets.
- original and actual CT3 research pair × 3 ratios, exactly 12 fits; preserve parent parameters/class weights.
- Original validation only for global Macro F1/Accuracy bands 1e-6, oldest control first. Known/stress excluded from selection; no test inference in runner.
- No production/CT1–CT3 modifications, deployment, CT5/Phase 6, commits, pushes, merges, publication or workspace cleanup.

## Review Focus

- Unsafe paths/symlinks rejected before writes or fitting; receipt payload paths cannot escape output.
- Augmented manifests describe actual training rows, inherited weak labels and original hash separately.
- Replay checks receipt schema/promotion, exact payloads, train-only vocabulary/IDF and immutable parent weights.
- Collision/conflict and cross-set normalized overlap recorded without filtering by validation labels.
- Joint accuracy derives from aligned per-row predictions and all transitions retained.

## Task 1 — transform, grouping and evaluation helpers

Files: reports/ct4_augmentation.py, tests/test_ct4_augmentation.py.
Interfaces: unaccent(text), augment_train(frame, ratio), select_candidate(metrics), comparison(before, after, validation).
- [x] Write tests for Unicode/idempotence, deterministic subsets/lineage, collisions, cloning and ranking/percentage/joint behavior.
- [x] Observe RED for missing CT4 module; save log.
- [x] Implement minimal pure helpers and clone fitting; verify GREEN.

## Task 2 — lifecycle and replay

Consumes Task 1 plus frozen CT1/CT2/CT3 interfaces; produces run_experiment(root, output, ct3_output=None), verify_experiment(root, output, ct3_output=None), CLI run/verify.
- [x] Write lifecycle tests using real controls and fixture without test split, forbidden fit during replay, output safety and tamper detection; observe RED.
- [x] Implement finite config/provenance/augmentation manifests, model metadata, full evaluation and semantic replay.
- [x] Verify scoped GREEN and frozen control preservation.

## Task 3 — actual experiment and handoff

- [x] Record preexisting hashes/status, run actual six pairs once and preserve incomplete runs.
- [x] Fresh-process verify without fitting, copy evidence, verify preservation.
- [x] Run full TV2_RUN_REAL_DATA=1 pytest including browsers and pip check; disclose warnings/failures.
- [x] Write report with all controls/candidates/selections, Accuracy/joint deltas vs Original and CT3, Macro metrics and per-class losses, collisions/stress/known cases/costs/limits.
- [x] Parent dispatches independent review; fix confirmed Important/Critical with regression tests, rerun affected checks/full suite as necessary.
