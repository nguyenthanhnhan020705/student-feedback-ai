# CT2 — Class-weight experiments implementation plan

> **For agentic workers:** Use superpowers:executing-plans; execute CT2 only.

**Goal:** Compare train-only class weighting with CT1 baseline-v2 on the same validation and known cases, preserving the serving models.

**Architecture:** Offline runner `reports/ct2_class_weights.py` reuses CT1 scoring, frozen pipelines and the canonical loader. Clone each baseline pipeline, change only classifier class_weight, fit train, evaluate validation/known cases, save local research artifacts and full regression evidence. Rank per task; combining rank leaders is a research result, never automatic deployment.

**Tech Stack:** Existing locked CPython 3.13, scikit-learn 1.6.1, joblib, pytest. No dependency changes.

**Spec:** `docs/quality/ct1-protocol.md`, the CT2 handoff in `reports/evidence/ct1/README.md`, and the user's “triển khai CT2”.

## Design and constraints

- Existing integration worktree; preserve dirty member work and all 49 CT1 protected inputs. No commit/push/merge/publication, CT3–CT5 or Phase 6.
- Scope already specified by the CT1 handoff and user's execution request; implement directly. Implementation choices below are the assistant's, not additional user decisions.
- Three fixed variants, set before looking at results: balanced weights N/(K*n_class), square root of those weights, and minority_x2 (neutral/other=2, others=1). All derive only from train labels. This small comparison isolates weighting; broad C/grid search and resampling introduce confounding/out-of-scope work.
- Clone fitted baseline to an unfitted pipeline; refit train only. No validation fit/refit, test inference or test-based selection. Keep normalizer, TF-IDF, C, seed and all other classifier parameters.
- Rank within 1e-6 of global maximum validation Macro F1, then within 1e-6 of global maximum eligible Accuracy, baseline then sqrt_balanced/balanced/minority_x2. Fixed maxima prevent pairwise tie-chain drift. Report every metric delta and all changed/regressed predictions. Known cases never decide rank; null expectations stay unscored.
- Research artifacts/metadata live under a fresh local run directory, never `models/`. Check full pipeline parameters against metadata, reload in a fresh process, evaluate exact replay. ModelService compatibility alone is not semantic validation.
- New final independent data is absent; no claim of independent improvement, fixed negation/emoji/OOD, or production promotion.

## Review focus

1. Weight computation must use only train and reject missing/unknown classes or other splits.
2. Ranking must not use known-case/test scores; ties must not replace baseline needlessly.
3. Regression comparison must preserve IDs, order, truth and null denominators; include correct-to-wrong and wrong-to-wrong changes.
4. Existing output/live-model paths must be refused before fitting/writing; incomplete runs cannot verify.
5. Replayed artifacts, metrics, source/runtime and metadata must be bound by hashes, not accepted merely because files exist.

## Task 1 — Weighting, fitting, ranking and regression safeguards

Files: `reports/ct2_class_weights.py`, `tests/test_ct2_class_weights.py`.

Interfaces: `class_weights(task, labels, strategy)`, `fit_candidate(baseline, train, task, strategy)`, `select_candidate(metrics)`, `compare_results(baseline, candidate, validation)`.

- [x] Write tests: hand-derived train weights, rejected split/labels, no validation vocabulary fit, unchanged baseline, ranking/ties, per-class negative deltas, null/changed/regressed rows and alignment errors.
- [x] Run RED for missing feature, implement, run GREEN plus CT1 tests.

## Task 2 — Reproducible local experiment and handoff

Files: same runner/tests; `docs/quality/ct2-report.md`, `reports/evidence/ct2/`, README and CT progress ledger.

Interfaces: CLI `run|verify --output <fresh run directory>`; final runtime default `.local-tools/ct2-class-weights/run-2` (run-1 preserved as review history).

- [x] Add RED tests for existing/live output refusal, replay/tamper failures and real fixture lifecycle without test data.
- [x] Implement new-run evidence, per-variant pipelines/metadata, combined research selection, hash receipt and no-fit replay.
- [x] Execute real run after CT1 verification; fresh-process replay, compatibility and CT1 preservation checks.
- [x] Run full suite with real-data flag and pip check; save logs, report real tradeoffs and deferred independent evaluation.
- [x] Independent fresh-context scoped review; resolve Important findings with regression tests. Update checklist/ledger, leave all work local.
