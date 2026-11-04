# CT4 independent-task demo implementation plan

> Use superpowers:executing-plans inline; TDD and fresh independent final review.

**Goal:** Trial CT4 demo with independent answered/insufficient decisions.
**Architecture:** Add demo_v2 backend/frontend on8001; preserve original source and
all frozen experiments. Reuse CT5 signals and frozen CT4/q10 files read only.
**Tech Stack:** Existing locked Python/FastAPI/sklearn/pytest/Playwright, plain JS.
**Spec:** docs/superpowers/specs/2026-11-01-ct4-partial-demo-design.md and user request.

## Constraints / review focus

No training/negation/aspect feature/Phase6/publication/commits. No overwrite of
existing files or baseline artifacts. Research q10 decision is provisional.
Review invalid/missing/tampered model and policy provenance; true per-task nulls;
Unicode/invalid JSON/error priority; zero word/nonzero char; body deadline and
unsafe or malformed partial labels. Preserve all CT1–CT5 original bytes.

### Task1 — policy, read-only CT4 service and API

Create demo_v2/{__init__,policy,service,main}.py; tests/test_demo_v2.py.
Produces factory create_app(service), service readiness/predict, decide_task.
- [x] Inventory every preexisting substantive file before new implementation.
- [x] Write RED policy/service/API tests including real artifacts, provenance failures,
      finite-gap guard, task-independent status and invalid input/error precedence.
- [x] Implement minimal policy/service/v2 API, scoped GREEN, no fitting.

### Task2 — frontend

Create demo_v2/frontend/{index.html,styles.css,api.js,app.js}; browser tests in
tests/frontend/test_demo_v2_ui.py. Consumes v2 contract produced by Task1.
- [x] Browser RED: real full/partial/insufficient, label type/prototype rejection,
      duplicate submits, body timeout/recovery, missing model, error/input lifecycle.
- [x] Implement frontend, Chrome/Edge GREEN and true screenshots/response evidence.

### Task3 — demo verification and handoff

Create reports/evidence/ct4-partial-demo/, docs/quality/ct4-partial-demo.md;
new verifier may live in evidence directory.
- [x] Record finite sample predictions and per-task/joint validation coverage/risk;
      no new threshold selection or fitting, independent evaluation pending.
- [x] Run full real-data/browser suite; preserve refreshed original screenshots.
- [x] Run no-fit CT5 replay and hash preservation; independent review, test-first
      corrections when required; keep old worktree/ledger and dirty work.
- [x] Start verified CT4 demo8001, check health/API/assets, supply link and limits.

No commit/merge/cleanup steps; user's local trial is the deliverable.
