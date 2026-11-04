# SDD ledger — plan: docs/superpowers/plans/2026-11-01-ct5-selective-prediction.md

Scope: user authorized CT5 milestone A per handoff on 2026-11-01. No B/Phase6/serving changes or Git publication.
Checklist: [ ] Task1 RED/GREEN; [ ] Task2 RED/GREEN; [ ] finite run; [ ] fresh no-fit replay; [ ] full suite; [ ] independent review; [ ] preservation/report.
Ruling: use approved handoff as design and existing linked feature/integration-p0; execute inline with one final independent reviewer — explicit scope already selected — no repeated design approval or additional worktree.
Ruling: persistent Windows-native plan/ledger, no Bash helper/commits/cleanup — user requires preserving dirty work — final deliverables remain local and uncommitted.
Pre-flight: Task2 consumes Task1 signal/policy/metrics interfaces; Task3 consumes Task2 deterministic run/replay; unchanged CT4 verifier supplies control provenance. No contract changes.
Status: initial inventory and baseline verification before implementation.

Task 1: complete — missing-module RED (red-task1.txt), GREEN 13 tests in 2.15s. Real word/char features, reordered classes, invalid scores, grouped partition, linear quantile, all-or-nothing and hand-derived metrics covered.
Initial preservation: 390 preexisting substantive files inventoried; JSON/PNG evidence bytes backed up. CT4 fresh control replay passed, original selected pair unchanged.
Task 2 RED: 5 failed / 13 passed / 23 errors, expected missing run/verify interfaces; serialized CT1–CT4 fixture built without test split. Implementation now under scoped tests.
Ruling: use fresh CT4 replay as control baseline and run full regression after CT5 — no production edits and expensive existing lifecycle suites — historical passing suite is not claimed as fresh CT5 evidence.

Task 2: complete — 41 passed in 57.34s (green-task2.txt), including serialized no-test-split fixture, no-fit run and fresh replay, path refusal, tamper and recomputed semantic checks. Four extra receipt-semantic cases and stricter rehashed-config assertions added for final suite; raw predictions invariant across policies.
Actual finite run: run-1 completed with all fit APIs forbidden, exit0. Two pairs x five policies, development792/audit791, 6 train/augmentation overlaps, no validation label-conflict groups. No policy selection, training or serving writes.
Fresh actual replay: exit0, verified=true, fit=false (replay.txt). pip check passed. Full real-data/browser suite in progress.
Expanded preservation inventory: 604 files including all CT1–CT4 local frozen payloads plus handoff; no existing file intentionally edited. Reports derive from recorded payloads; independent review dispatched read-only while final suite completes.

## Final completion — CT5 milestone A

Task 3: complete — finite run and fresh no-fit replay exit0; full suite351 passed/0 skipped/14 existing warnings in320.24s; pip check exit0. Preservation604/604 hashes, zero changes/restorations; six browser outputs copied separately. No code changed after actual run.
Final independent review: ct5_review found no Critical/Important; independently checked8 payload hashes, source/data hashes, all12 thresholds and40 summaries including per-class/confusion arithmetic. Parent final suite/preservation satisfy review conditions.
Final: minor (deferred): finite extreme scores can overflow derived gap in direct helper; actual stored gaps finite and no completed JSON receipt can contain infinity. No current artifact/result affected; disclosed in report/review.
Final: Ruling: independent semantic/OOD performance remains pending — no human-reviewed final or answerability data exists — no false-reject/unsafe-accept/generalization certification.
Final: Ruling: production readiness and old CT3/Backend minors remain outside A — no policy selected or API/model/control changed — milestone B requires separate contract approval, old defensive limits retained.
Checklist: [x] Task1 RED/GREEN; [x] Task2 RED/GREEN; [x] finite run; [x] fresh no-fit replay; [x] full suite; [x] independent review; [x] preservation/report.
Status: engineering_complete_independent_evaluation_pending, recommended_policy=null, needs_coverage_risk_decision, not_deployed. No Phase6, commit/push/merge/publication or worktree cleanup.

Final inventory correction: initial604 inadvertently included the newly-created CT5 plan (inventory occurred after plan creation). Final audit caught its expected checklist update. Preserve initial inventory separately; exclude only that new plan, retain every original expected hash. Correct preexisting count603; no original bytes changed. Re-run preservation and handoff audit, no production/code/result changes. Earlier604 references are historical overcount, superseded by this correction and final603/603 preservation.
