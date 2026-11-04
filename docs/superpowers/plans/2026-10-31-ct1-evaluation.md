# CT1 — Evaluation baseline implementation plan

> **For agentic workers:** Use superpowers:executing-plans. Execute CT1 only, as explicitly requested by the user.

**Goal:** Freeze the current baseline and provide repeatable validation and known-case evaluation for CT2–CT5.

**Architecture:** Offline tools under reports/; canonical labels and frozen pipelines are reused. No change to application behavior or original evidence. Snapshot local artifacts, code/data hashes and metric inputs. Evaluate validation and diagnostic cases, never train or use test for selection.

**Tech Stack:** Existing locked Python 3.13, joblib, scikit-learn, pytest.

**Spec:** docs/quality/ct1-protocol.md; user's CT1 authorization and five-phase outline in conversation.

## Global constraints

- Keep the existing linked integration worktree; preserve all pre-existing work.
- Do not train, change models/preprocessing/API/UI, start CT2 or Phase 6, commit/push/merge.
- Corpus/model snapshots stay local; no publication authorization.
- No invented independent/human-reviewed evaluation data.

## Review focus

- Missing/invalid class predictions must fail, not disappear from metrics.
- Null/ambiguous expected labels must not count as correct or incorrect.
- Artifact/data changes and accidental overwrite must fail visibly.
- Candidate comparisons must use the same corpus, cases, policy and label order.
- Validation development results must not be described as final independent quality.

## Task 1 — Evaluation tool and safeguards

Files: reports/ct_evaluation.py, tests/test_ct_evaluation.py.
Interfaces: score_labels(truth, predictions, labels); score_cases(cases, predictions);
verify_inventory(root, inventory); create_baseline(root, output); verify_baseline(root, output).

- [x] Write tests for invalid/aligned predictions, ambiguous expectations, tampering and overwrite refusal.
- [x] Run tests RED; implement metrics, frozen snapshot creation and verification.
- [x] Run tests GREEN, real baseline creation and replay; compare validation metrics with frozen comparison.json.

## Task 2 — Evaluation protocol, cases and handoff

Files: docs/quality/ct1-protocol.md, reports/quality/known-cases.json,
reports/evidence/ct1/, docs/superpowers/plans/ct-progress.md.

- [x] Label known cases from the prior diagnosis with explicit assistant-authored provenance;
  ambiguous tasks use null; group counts and exact results are reported separately.
- [x] Define per-task validation selection, regression reports, no automatic deployment,
  and independent final-data collection/review protocol.
- [x] Freeze baseline and case outputs; verify reproducibility and unchanged source hashes.
- [x] Run relevant tests, independent scoped review, address findings, record limitations.
