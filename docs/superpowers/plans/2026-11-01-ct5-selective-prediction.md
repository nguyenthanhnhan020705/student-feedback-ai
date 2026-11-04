# CT5 selective prediction offline — Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans task-by-task. User selected the detailed CT5 handoff; no repeat design approval, commits, branch cleanup or production changes.

**Goal:** Complete milestone A: reproducible offline coverage/risk evaluation without fitting or replacing classifiers.

**Architecture:** Read-only original and CT4 research-selected pipelines, shared score extraction, group-hash validation partition, five fixed policies per pair. Write a fresh research run with deterministic payloads and a receipt; recompute everything in a fresh no-fit process.

**Tech Stack:** Existing locked Python 3.13, NumPy, SciPy, sklearn, pandas, pytest. No new dependencies.

**Spec:** docs/quality/ct5-agent-handoff.md (user selected), docs/quality/ct1-protocol.md, API/data contracts 1.0.

## Global Constraints

- Offline only; original and CT4 pair, 5 policies each: always_answer, zero_features, zero_plus_margin_q05/q10/q20.
- Quantile method='linear'; task/model-specific thresholds from nonzero threshold-development rows only.
- group_key=normalize_text(unaccent(text)); SHA256('ct5-v1|42|'+group_key); first byte <128 is development, otherwise audit.
- No training, calibration, extra configurations, test-based selection, new dependency, source/model/API/UI edit, CT6/Phase6, commit/push/merge or publication.
- Null truth excluded from correctness denominators, never from input coverage; rejection is not correctness; margin is not probability.
- recommended_policy=null; needs_coverage_risk_decision; engineering_complete_independent_evaluation_pending without human-reviewed final data.

## Review Focus

1. FeatureUnion has a zero word branch but nonzero character branch: accept according to the complete feature vector.
2. Bad score/class shapes, nonfinite values, or prediction disagreement: fail rather than abstain.
3. Missing truth and empty accepted subsets: explicit denominators and null metrics, including missing classes.
4. Coherent tampering with rehashed receipt: recompute split, thresholds, predictions and all metrics, validate receipt semantics.
5. Junction/symlink paths and nested receipt files: reject redirected research paths and exact membership differences before writes/loads.

### Task 1 — Scoring, partition, policy and metrics

**Create:** reports/ct5_selective_prediction.py; tests/test_ct5_selective_prediction.py.
**Interfaces:** extract_signals(pipeline,texts,task); partition_validation(frame); fit_thresholds(signals,indices); apply_policy(rows,signals,policy,thresholds); summarize(decisions).

- [x] Write tests: real word/char pipelines, classes order, bad scores, gap boundary, quantile/no signal, grouped split/empty side, all-or-nothing, hand-derived C/A/E/N, missing truth and answerability.
- [x] Run RED, record intended missing-module/API failures.
- [x] Implement only tested behavior; run scoped GREEN.

### Task 2 — Read-only lifecycle and replay

**Create:** lifecycle in runner, lifecycle tests, reports/evidence/ct5/.
**Consumes:** Task 1 interfaces, unchanged CT4 verify and ModelService; produces config/partition/thresholds/decisions/metrics/status/receipt.

- [x] Tests first: serialized real pipelines with no test split; forbid fit in run/replay; fresh paths, source/model/control/runtime/payload tamper, nested receipt and rehashed semantic tamper.
- [x] RED then implementation then GREEN; frozen control chain must replay unchanged.
- [x] Receipt binds all payloads, code/runtime/control/model/source hashes and exact semantics; replay compares freshly derived payloads.

### Task 3 — Finite run, verification and handoff

**Create:** docs/quality/ct5-report.md, ct5-data-requirements.md; evidence and ct5-progress.md.
**Consumes:** verified runner, existing originals/CT4, preservation inventory.

- [x] Freeze configuration before actual scoring; run 2 pairs x 5 policies only. Separate audit, development, ungated full-validation, known groups and synthetic stress.
- [x] Fresh process replay with fit forbidden; record hashes and missing independent-label status.
- [x] Backup preexisting browser evidence, full suite with real data/browser, pip check; retain refreshed browser outputs in CT5 and restore only changed original bytes.
- [x] Fresh-context independent review of CT5 scope; test-first fixes if required; reverify affected evidence.
- [x] Final preservation hashes, report full coverage/risk denominators, proposed milestone B schema/message as proposal only, no deployment choice.

No commit steps: explicitly forbidden by user. Preserve worktree and ledger for later work.
