# SDD ledger — plan: docs/superpowers/plans/2026-11-04-standalone-project.md

Execution: native, approved by user. BASE f91f10b; existing linked worktree chore/project-cleanup.
Tasks 1–7 pending. No changes to old source allowed.
Preflight interfaces: Settings feeds bundle/API/CLI; FrozenModels feeds AnalysisService; API and IO feed frontend; shared data/metrics feed training and experiments. No conflicting signatures found.
Ruling: use this persistent ledger instead of Bash workspace helper on Windows; artifacts stay in ignored outputs or .local-tools. Keep compatibility modules only for frozen pickle callback paths. Independent final review required.

## Execution 2026-11-04 (continuation)
- Reality check: Tasks 1-6 code existed uncommitted (ledger above was stale); 187 unit tests passed/3 skipped (real-data flag), commit 51fb9d6.
- Ruling: pytest needs `--basetemp=outputs/tmp-pytest` — system temp pytest-of-DELL is access-denied here — cost: none.
- Ruling: web assets stay as the byte-identical legacy JS files (api/app/batch.js), not split into modules — spec says refactor must not change behavior and plan's split is optional "implementer decides"; cost: less modular JS.
- Real CLI verified: data validate/eda, train topic+sentiment, evaluate topic (fresh outputs); real bundle serves health/predict/import/export.
- Task 3/4 parity: tools/capture_baseline.py recorded 30 legacy cases -> tests/parity/baseline.json; 31 parity tests pass; negative control (edited baseline) fails as expected.
- Task 5 browser: tests/browser (Chrome+Edge) 26 pass: labels, health fail/recovery, tab keyboard, paste/CSV/XLSX, export-all-while-filtered, row failure, mobile overflow.
- Task 2 integration: tests/integration/test_bundle.py (6 pass): checksum verify, tamper/missing rejected, broken bundle -> ready=false + UI 200 + 503, subprocess with no PYTHONPATH loads shims from project/env only, audit-hook negative control catches legacy access.
- Task 6: configs/*.json; all five experiments run for real (baseline, class_weights, word_char chained from class_weights, augmentation chained from both, selective); none beat the frozen control on validation (docs/evaluation.md). tools/fill_checksums.py fills chain checksums. Notebooks 01-03 rewritten onto feedback_ai and executed cell-by-cell in tests (real data). tests/integration/test_workflows.py: train+evaluate leave serving hashes unchanged, overwrite/serving paths refused, tampered artifact rejected, wheel contains rules/web/shims (6 pass, 204s).
- Ruling: notebooks avoid IPython (not in lock) — use matplotlib for the confusion matrix image; cost: none.
- Ruling: integration/parity/browser fixtures FAIL when bundle/data/browser missing rather than skip (spec: skip is not success); cost: plain `pytest` on a bare clone fails until data/bundle are imported — documented in README/docs/operations.md.
- Ruling: word_char/augmentation configs use outputs of earlier experiments as CT2/CT3 controls (the old CT2/CT3 candidate artifacts are not bundled); cost: their results differ from historical CT2/CT3 runs only if those used other weights — both selected baseline here.
- Task 7: tools/verify_standalone.py written; run recorded below.
- Task 7: verify_standalone run2 (fresh venv from lock + wheel, no PYTHONPATH, cwd outside project): all 16 steps ok — module origins in venv, serve health ready + predict mixed/[lecturer,facility], data validate, train+evaluate topic (acc 0.86166), pytest unit+integration+parity 233 passed, bundle bytes unchanged, legacy source hashes unchanged. Report: .verify/run2/report.json (scratch, untracked).
- Finding fixed in Task 7 by that run: 3 real-data tests read legacy `reports/data/*` and the isolation negative control was inert outside the old checkout; now project-relative `data/source.json|manifest.json` and a simulated old checkout. `data validate` now records data/source.json provenance when present.
- Full suite in project venv with TV2_RUN_REAL_DATA=1: 259 passed, 0 skipped (unit, integration, parity, browser Chrome+Edge).
- Final review: dispatched fresh reviewer (opus) at commit f351220; findings pending.
- Final review: reviewer agent was stopped by the user before reporting; NO review findings exist. Review not done; work is unreviewed by a fresh context.
