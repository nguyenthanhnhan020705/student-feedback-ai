# CT5 independent fresh-context review — 2026-11-01

Reviewer: separate read-only ct5_review agent. No files modified, no fitting,
and no independent rerun of expensive replay/full suite by reviewer.

## Verdict

Implementation and recorded results acceptable with one defensive Minor.
No Critical or Important CT5 finding. Review's final completion condition:
parent must confirm running full suite and final preservation check.

## Independently checked

- All eight run receipt payload hashes and exact membership; source/data hashes.
- Hash partition membership and absence of cross-partition groups.
- All 12 model/task linear-quantile thresholds.
- All 40 model/dataset/policy summaries, joint arithmetic, raw-prediction
  invariance, decisions, null/display behavior and per-task confusion/per-class metrics.
- Same 791 audit IDs: Original always A791/C653/E138, q10 A635/C571/E64;
  CT4 always A791/C649/E142, q10 A646/C574/E72.
- Complete-vector gating, missing-truth denominators, all-or-nothing labels,
  replay recomputation, redirected-path refusal and nested receipt membership.

## Minor — deferred defensive finite-gap check

reports/ct5_selective_prediction.py:80: finite extreme scores
`[-1e308, -1e308, 1e308]` overflow subtraction to infinite gap. A read-only,
no-fit in-memory probe confirmed extract_signals returns it and apply_policy
accepts that row. Explicit finite-gap guard and scoped regression are suggested.

This does not invalidate saved run-1: every saved gap is finite;
fit_thresholds rejects nonfinite development gaps and JSON serialization
allow_nan=False prevents a completed run/receipt containing infinity.
Parent retains this as a defensive minor for direct-helper/extreme-score use,
not a current-artifact correctness blocker. No rerun/tuning to hide a finding.

## Declined to certify

- Unfinished full-suite execution and final 603-file preservation at review time:
  parent verifies these from actual final logs/hashes below, not from this verdict.
- Independent semantic/OOD performance: no human-reviewed final/answerability set.
- Production readiness: milestone A only; no selected policy or API migration.
- Existing CT3/backend minors: unchanged frozen controls outside CT5 scope.

Keep engineering_complete_independent_evaluation_pending and recommended_policy=null.
Recorded no-fit replay passed. Review is based on source, saved evidence,
independent arithmetic/hash checks and the extreme-score probe.

## Parent closure after review

Full-suite process exited 0: **351 passed, 0 skipped, 14 existing warnings**,
320.24s. pip check exit0. Post-suite preserve.py exit0 confirms **603/603
preexisting hashes**, zero changed and zero restorations needed; six refreshed
browser JSON/PNG artifacts retained separately under CT5/browser.
Review completion conditions are satisfied by these parent-run checks, not
claimed as an additional independent suite/review. No code fixes after review;
the defensive minor remains disclosed. No serving/Git/publication changes.
