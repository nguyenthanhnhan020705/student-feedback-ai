# CT5 milestone A evidence — 2026-11-01

Engineering complete; independent evaluation pending. recommended_policy=null,
needs_coverage_risk_decision, not_deployed, offline_research_only.

Authoritative run: `.local-tools/ct5-selective-prediction/run-1/` relative to
integration-p0. Full per-row diagnostics/decisions (about 66 MB) stay there,
alongside partition/group/overlap, all metrics, thresholds and receipt.
This directory contains compact copies and verification/handoff evidence;
run receipt payload paths are relative to the authoritative run, not here.

## Checks actually run

- red-task1.txt: expected missing module; green-task1.txt: 13 passed.
- red-task2.txt: expected missing run/verify APIs, 5 failed/13 passed/23 errors.
- green-task2.txt: 41 passed, 57.34s. Additional four receipt semantic cases
  and stronger config/raw-prediction assertions included in final suite.
- run-1.txt: 2 pairs x 5 policies, with all relevant fit APIs forbidden.
- replay.txt: fresh process no-fit replay exit0, verified=true; exact partition,
  thresholds, scores, decisions, metrics and receipt checks.
- full-suite.txt: **351 passed, 0 skipped, 14 existing warnings**, 320.24s, exit0.
- pip-check.txt: no broken requirements.
- preservation.json/txt: **603/603 original hashes match**, zero restoration;
  six browser outputs copied into browser/, originals retain exact bytes.
- review.md: separate read-only reviewer, no Critical/Important finding;
  independent arithmetic and hashes; one deferred defensive overflow minor.

No new dependencies, classifier fits, serving replacements or API/UI edits.
No Phase6, commits/pushes/merges or publication. Suite's historical test use
is regression only; CT5 runner does not infer/test-select on historical test.

## Reproduce

From integration-p0:

```powershell
./.venv/Scripts/python.exe -B reports/evidence/ct5/no_fit.py verify
```

`run --output .local-tools/ct5-selective-prediction/<fresh-name>` refuses existing,
live and redirected research outputs. It does not train or copy serving models.
no_fit.py bans Pipeline/FeatureUnion/vectorizer fit/fit_transform and LinearSVC.fit.
Fixture lifecycle tests serialize real models before the CT5 no-fit phase, and
have no test split on disk. Tamper cases cover data/model/control/runtime/source,
config/partition/threshold/prediction/metrics/status/receipt, coherent rehashes,
incomplete runs, exact membership and nested receipt.json.

`render_report.py` renders recorded numbers/figure; `preserve.py` retains browser
refreshes and restores only verified original browser bytes if necessary.
Original evidence backup stays at `.local-tools/ct5-preexisting-backup/`.

## Limits

Development792/audit791 both come from repeatedly exposed validation. Six
unaccented train overlaps, known assistant-proposed labels and inherited stress
labels are disclosed. No human-reviewed independent final/answerability set;
semantic false reject/unsafe accept remain unmeasured. Margin is not probability;
rejecting is not a correct prediction. See docs/quality/ct5-report.md and
ct5-data-requirements.md, plus review.md for the finite extreme-score gap minor.

No policy chosen. Milestone B API/schema/UI integration requires separate user
approval; the report contains a labeled proposal only.
