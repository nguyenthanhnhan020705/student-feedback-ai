# CT4 independent review

Status: initial source review; final run/replay/full-suite/report evidence pending.

Scope: CT4 handoff and plan, reports/ct4_augmentation.py, tests/test_ct4_augmentation.py, and referenced CT1–CT3 controls. No production files modified; no suite rerun.

## Critical

None identified.

## Important

1. **Lifecycle fixture does not exercise augmentation** — tests/test_ct4_augmentation.py:108–117. The fixture invokes the unchanged CT2 small_project helper, which builds ASCII-only texts. Despite its comment, it never intercepts source construction. All ratios therefore add zero rows and the lifecycle/replay/tamper tests miss actual augmented training vocabulary, IDF, and nonempty lineage manifests. Remedy: create accented source before the CT1 freeze without modifying CT2, and assert each manifest has positive added_rows and training_rows greater than source_groups. Pure transformation tests do not replace this lifecycle coverage.

## Minor

1. **Nested receipt filenames evade exact inventory membership** — reports/ct4_augmentation.py:393. The filter excludes every file named receipt.json rather than only the root receipt. An extra output/extra/receipt.json is consequently invisible to exact payload membership verification. Remedy: exclude only output/receipt.json and add a nested extra-file tamper case.

## Initial assessment

The reviewed implementation uses deterministic nested train-only subsets, preserves parent parameters and class weights via cloning, reconstructs training vocabulary/IDF without fitting during verification, replays frozen controls, checks CT4 receipt schema/promotion, uses fixed global tie bands, aligns joint predictions to source IDs, and separates synthetic stress from selection. No further concrete correctness finding identified in this pass. Approval remains pending fixes and final evidence review.

## Scoped re-review after fixes

Both initial findings are addressed in the current source:

- Important lifecycle gap: resolved by a CT4-local fixture that writes accented train before freezing CT1/CT2/CT3 controls. The lifecycle test asserts positive added_rows and training_rows > source_groups at all three ratios (tests/test_ct4_augmentation.py:198–202).
- Minor payload membership gap: resolved by excluding only the root receipt (reports/ct4_augmentation.py:393); a nested_receipt tamper case adds extra/receipt.json and requires rejection.

Reviewed review-fixture-red.txt and review-payload-red.txt: failures demonstrate the intended missing augmentation and previously accepted extra payload, respectively. No additional source blocker identified before freezing the runner hash. Final experiment/replay/full-suite/report evidence review remains pending; suite was not independently rerun during this review.

## Actual-run evidence review

Reviewed actual .local-tools/ct4-augmentation/run-1 payloads and report. Independent read-only SHA-256 checks confirm all 41 receipt payload hashes and runner hash match; receipt semantics are ct4.1 / not_deployed / research_only. There are exactly 12 fit records across six pairs. Source/eligible/added/training counts, 33 transformed collision groups and 5 conflicting-label groups match report. Selection and Accuracy/joint percentage-point and relative deltas agree with stored results; joint is 1292/1583, four fewer correct rows than Original and one more than CT3. Synthetic stress and provisional known-case denominators remain separate from selection and original validation.

Reviewed recorded fresh replay (verified true), scoped GREEN (25 passed), and pip check (no broken requirements). Independent rehash of preexisting.json at review time confirms 335/335 files unchanged. Full-suite evidence is still running at this point; final completion is not yet certified.

Residual Minor: docs/quality/ct4-report.md topic per-class rows in both selected sections lack a Markdown table header after the intervening sentiment matrix paragraph. Emit the header for each task in render_report.py so topic rows render as a table. No residual Critical or Important finding identified.

## Final completion assessment

Final recorded full-suite result: **306 passed, 14 known warnings, no skipped**, in 227.62s (full-suite.txt). Warnings are the existing Starlette/httpx deprecation and scipy optimizer iprint warnings; no dependency upgrade was used. Recorded pip check and fresh replay pass. The final report now emits separate valid table headers for both tasks, resolving the formatting minor.

After the suite completed, I independently recalculated every SHA-256 in preexisting.json: **335/335 match, zero differences**. This confirms preserved preexisting source/evidence bytes at final review time, including serving artifacts. Reviewed the additional overlap audit: six stripped-text validation overlaps, zero cross-set label conflicts; the report correctly treats stress as non-independent and does not use it for selection.

**Residual findings:** Critical: none. Important: none. Minor in CT4: none. Initial findings above remain as review history and are resolved. Existing CT3 receipt-semantics and backend lone-surrogate minors remain explicitly deferred outside CT4 scope.

**Assessment:** Approved for completion of the authorized local, offline CT4 experiment and handoff. This assessment does not authorize deployment, serving-model replacement, publication, commits, pushes or merges. Validation remains repeatedly exposed; augmented labels are inherited weak supervision, exact overlaps do not establish absence of near-duplicates, and the observed Macro F1 improvement does not establish an overall Accuracy/joint improvement over Original. Review used the recorded suite/replay evidence plus independent lightweight source, hash and numerical checks; the costly suite was not rerun by the reviewer.
