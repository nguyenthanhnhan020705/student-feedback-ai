# TV4 Topic completion ? 2026-10-29

Authority: approved docs/specs/data-contract.md v1.0 and docs/topic/README.md.
User requested completing TV4 after reviewing current local Data/Sentiment.

Approach: extend existing TV4 commit 74330f3, preserving its separate Topic modules.
Do not replace it with Sentiment code or introduce shared training abstractions.
Work in the current checkout to consume the uncommitted Data handoff. No branch switch,
commit, push or changes to Data/Sentiment files. Use existing Python 3.13 ML environment;
record exact packages, without claiming a leader-approved lock or Data license approval.

## Tasks
- [x] Restore existing Topic modules; add fixture tests for all four classes, train-only
  vocabulary, validation-only selection/ties, metrics orientation and prediction inputs.
- [x] Add CLI/artifact lifecycle tests (new process reload, checksum/environment failures,
  output isolation, actual dataset manifest linkage). Observe failures before fixes.
- [x] Complete training CLI, portable outputs and verification as tests require.
- [x] Run real baseline once, freeze winner by validation, generate test comparison,
  confusion matrix, error analysis, reload evidence and executed notebook.
- [x] Run project regression tests, independently review Topic changes, document measured
  results, reproducible commands and pending integration/review requirements.

## Verification
Use .venv/sentiment/Scripts/python.exe with tests/test_topic*.py, then all tests/ with
TV2_RUN_REAL_DATA=1. Fixture lifecycle outputs must stay in pytest temporary directories.
Actual runs write only Topic-owned models/reports/notebook/docs. Do not publish corpus text.
Review focus: metadata vs actual data, test-set isolation, rerun behavior, evidence provenance,
rare-class and multi-topic analysis, no collateral edits to existing local work.

## Execution evidence
- Recovered upstream Topic modules without changing Git branch/index or unrelated files.
- Initial Topic run: 16 passed, 2 failed (missing manifest/figure CLI options).
- Added CLI paths and verified actual corpus against manifest; Topic suite: 18 passed.
- Real frozen winner: linear_svm, validation Macro F1 0.754173; test Macro F1 0.735382.
- Notebook: 4 plain-Python cells executed, no error outputs; no notebook dependencies installed.
- Full tests/ regression: 63 passed, no skips; 11 existing-library OptimizeWarnings.
- Fresh-process serialization round-trip and full test metrics match frozen comparison.
- Independent review found one Important metadata-schema gap; regression test reproduced
  acceptance of empty parameters, invalid timestamp and missing validation metrics.
  Fixed validation of nested metrics, UTC timestamp and actual pipeline parameter agreement.
  Final full tests/ run: 63 passed, 11 library warnings, no skips; notebook rerun 4 cells/0 errors.
- Review found no Critical issues and no other concrete issues. No second review was run;
  the fix was checked by the regression suite and real-artifact notebook execution.
- Reviewer left Backend integration, redistribution approval and historical decision timing
  unjudged: integration/approvals remain pending; this run used the pre-existing v1.0
  configurations and selection rules before the one real training run, with no test tuning.

Decisions: preserve local workspace because required Data is uncommitted; reuse installed
ML environment without upgrading it; retain upstream refusal to overwrite baseline files.
All three choices and their integration limits are documented in experiment.md/report.md.
