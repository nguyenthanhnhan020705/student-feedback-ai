> **Lưu trữ lịch sử:** tài liệu này không điều khiển tiến độ hiện tại. Xem kế hoạch sáu phase ngày 2026-10-30 và README tổng.

# P0 completion implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement task-by-task.

**Goal:** Deliver the approved P0 application, real-model integration, reproducible environment and evidence-backed report/presentation.
**Architecture:** Preserve the Data/Sentiment/Topic work in the main checkout. Import Backend from its local worktree and Frontend from its feature branch into an isolated integration worktree, together with uncommitted ML work. Keep all original work untouched.
**Tech Stack:** CPython 3.13, scikit-learn 1.6.1, FastAPI, plain HTML/CSS/JS.
**Spec:** docs/specs/mvp.md, api-contract.md, data-contract.md, environment.md.

## Global constraints
- P0 only; P1 needs separate permission. No publish, approve, merge or direct push to main/develop.
- Preserve existing work and real frozen experiments. Do not tune on test or invent metrics.
- Input maximum 5000 Unicode code points; UI timeout 10000 ms; two real models required.
- Dataset license remains unknown until supported by source evidence; user approval cannot substitute for a license.

## Review focus
- Real artifacts must load with exact training package versions and produce the same labels through API.
- Missing/corrupt artifacts must leave health available and predictions unavailable.
- Unicode, malformed JSON, wrong types and unexpected model outputs must preserve error contracts.
- Browser must retain input on errors, clear stale results, prevent duplicate requests and recover after reconnect.
- Clean environment and non-root working directory must preserve model/static paths.

## Tasks
- [ ] 1. Preserve source inventories and assemble isolated integration checkout; verify baseline suites, provenance and dataset licensing evidence.
  Files: existing backend/frontend/ml/tests/docs, reports/evidence/phase-6/source-inventory.json.
- [ ] 2. Resolve a common environment retaining the five exact ML package versions in both metadata files; install clean environment, pip check, record full locks.
  Files: requirements*.txt, pytest.ini, .env.example, docs/development.md.
- [ ] 3. Add real-artifact integration tests before fixing integration defects. Assert health ready, API/direct prediction equality, valid static assets, missing/corrupt models and portable paths. Run existing suites and new tests.
  Files: tests/integration/test_prediction_flow.py, backend/* only where reproduced failures require changes.
- [ ] 4. Add browser tests for real inference and controlled error responses, Unicode boundaries, timeout, duplicate clicks, reconnect and stale results. Fix demonstrated UI defects. Capture real Chrome/Edge versions and screenshots.
  Files: tests/frontend/test_ui.py, frontend/*, reports/evidence/frontend/*.
- [ ] 5. Reconcile documentation, acceptance matrix, scaffold inventory and contribution provenance. Produce final-report.docx and presentation.pptx from measured results, plus demo script and known limitations. Verify artifacts open structurally and links resolve.
  Files: README.md, docs/* status documents, reports/final-report.docx, reports/presentation.pptx, reports/demo-script.md, reports/contributions.md.
- [ ] 6. Run complete suite in clean locked environment, record actual timing and acceptance evidence, independent final review and regression fixes. Deliver local reviewable result; retain unresolved external approvals explicitly.

## Execution rulings
- User explicitly requested completing the approved project and filling all gaps; proceed with existing approved design without another design approval round.
- Use inline implementation and one final independent review. Preserve originals and do not commit their work implicitly.
- Publication/legal approval and academic submission schedule remain external conditions; continue all independent technical work.
