# SDD ledger — plan: docs/superpowers/plans/2026-10-31-ct4-augmentation.md

Scope: user selected and authorized handoff design, CT4 offline only.
Ruling: reuse existing linked feature/integration-p0 and native Windows ledger; no commits/cleanup — preserve all dirty work — delivery remains local.
Ruling: execute detailed approved handoff without repeat design approval; include synthetic unaccented validation stress separately — directly measure robustness without selecting on stress — inherited labels remain weak supervision.
Pre-flight: Task 2 consumes Task 1 transformation/selection and existing CT1–CT3 replay; compatible interfaces. Task 3 consumes run/replay and evidence; no production API changes.
Status: plan saved before tests/code; implementation in progress, independent review pending.
Task 1: complete — RED missing CT4 module, GREEN 6 tests (green-task1.txt).
Task 2: lifecycle RED 16 expected missing-API failures, 7 passed; initial GREEN 23 tests.
Review fix: local lifecycle controls originally ASCII so no augmented rows; regression requiring positive additions failed (review-fixture-red.txt). CT4-local accented source fixture now freezes controls only after writing accented train; CT2 helper unchanged.
Review fix: nested extra/receipt.json previously escaped payload-membership inventory; test failed as expected (review-payload-red.txt). Exclusion now applies only to top-level receipt. Full scoped GREEN running.
Ruling: preserve integration README unchanged to keep all 335 preexisting source/evidence hashes stable; use CT4 report and ledger as handoff entry points.
Task 2: complete — final accented lifecycle and nested receipt fixes GREEN 25 passed, no skips/warnings, 113.67s (green-task2-reviewed.txt). No old runner changed.
Task 3 actual run: complete — six fixed pairs, 12 fits, no fit warnings; source groups 11426, eligible11411, added2852/5705/11411. No extra tuning.
Fresh-process replay: PASSED with Pipeline.fit and LinearSVC.fit forbidden; exit0 (replay.txt). Checks control chain, all artifacts/combined pairs and augmented manifest/params/vocabulary/IDF/metrics/ranking/deltas.
Result: all-control and CT4-only select sentiment ct3parent_aug100 + topic ct3parent_aug25. Accuracy91.2824%/87.8711%, joint1292/1583=81.6172%. Compared Original Accuracy/joint -0.1895/-0.1263/-0.2527 pp; compared CT3 +0.1895/+0.0632/+0.0632 pp. MacroF1 79.7398%/76.9484%; not an overall improvement over Original.
Ruling: record 33 stripped-text collision groups, 5 label-conflict groups and six unaccented validation overlaps without filtering train — handoff requires report-only — synthetic stress is contaminated by exact stripped-text overlap and not independent.
Ruling: back up preexisting byte inventory before full regression because existing browser tests refresh historical screenshots; retain refreshed copies under CT4, restore originals afterward — preservation exceeds default test behavior — CT4 evidence points to copies rather than overwriting history.
Full real-data/browser suite running; pip check PASSED. Independent review performed by parent-side reviewer; final review receipt and suite/preservation still pending.

## Final completion

Task 3: complete — full real-data/browser suite 306 passed, 0 skipped, 14 known warnings in 227.62s; pip check passed. Actual run and fresh no-fit replay exit0. No redundant suite after documentation-only completion.
Independent review: approved; no remaining CT4 Critical/Important/Minor (reports/evidence/ct4/review.md). Both initial findings fixed by RED→GREEN: accented lifecycle and nested-receipt membership; report table formatting resolved.
Preservation: all 335 preexisting source/evidence hashes match; original bytes required no restoration. Browser evidence copied into CT4/browser. CT1 live/snapshot 49 files each, CT2 19 payloads, CT3 31 payloads and CT4 41 payloads checked. Serving models and all old runner sources unchanged.
Final: minor (deferred outside CT4): existing CT3 receipt schema/promotion replay gap and Backend lone-surrogate detail field remain unchanged/disclosed.
CT4 COMPLETE within offline research scope. No serving replacement, CT5/Phase6, commit/push/merge/publication or cleanup. Validation evidence does not establish independent generalization.
