# CT4 evidence — train-only unaccented augmentation

Actual run: `.local-tools/ct4-augmentation/run-1/`; report: `docs/quality/ct4-report.md`.
Serving models unchanged. All datasets/artifacts remain local; source license unknown.

- red-task1.txt: missing CT4 module before implementation; green-task1.txt: 6 passed.
- red-task2.txt: missing lifecycle APIs, 16 failed/7 passed as expected.
- green-task2.txt: initial 23-test pass using ASCII lifecycle; superseded by accented lifecycle below.
- review-fixture-red.txt: positive augmentation assertion failed on old ASCII fixture.
- green-accented-fixture.txt: 24 tests passed with accented source frozen before controls.
- review-payload-red.txt: nested extra/receipt.json membership regression failed before fix.
- green-task2-reviewed.txt: final 25 passed, no warnings/skips, 113.67 seconds.
- run-1.txt: six candidate pairs / exactly twelve real train-only fits; no extra configurations.
- config.json/results.json/summary.md/receipt.json: copies of official run evidence.
- provenance.json: augmented manifests/counts/checksums and complete lineage without raw source text.
- collisions-*.json: exact normalized and unaccented overlap/collision/conflict audit, report-only.
- replay.txt: fresh Python process replay with BOTH Pipeline.fit and LinearSVC.fit forbidden;
  verifies control chain, all twelve artifacts, selected pairs, exact metrics/ranking/deltas,
  augmented vocabulary/IDF, parent parameters/weights, lineage and receipt semantics.
- full-suite.txt: full real-data/browser suite; final result must be read from log tail.
- pip-check.txt: existing locked dependencies, no upgrade.
- preexisting.json/git-status-before.txt: 335 preexisting source/evidence file hashes and dirty status.
- preservation.json: final verification of those bytes plus CT1/CT2/CT3 payloads, written after suite.
- review.md: independent review by separate reviewer, recorded by parent agent.

The synthetic unaccented validation stress uses the SAME validation source groups,
weak inherited labels, and never affects ranking. The 39 diagnostic cases retain
assistant-proposed labels with null excluded by task; neither is independent data.

Full regression suite may re-evaluate historical test artifacts. CT4 run/replay
does not infer/read test for candidate ranking. Browser tests can refresh historical
screenshots; original bytes are backed up locally, refreshed copies retained under
CT4 if changed, then restored to preserve all preexisting work.

No commit/push/merge/deployment/CT5/Phase6/publication. Dataset-containing augmented
manifests and model binaries are NOT copied into this evidence directory.

## Final verification

306 passed, 0 skipped, 14 known warnings in 227.62s; pip check and fresh no-fit replay passed. Independent review approved, no CT4 findings remain. Preservation: 335 preexisting files, CT1 live/snapshot49 each, CT2 payload19, CT3 payload31, CT4 payload41 all match. Browser evidence copied to browser/; original bytes already matched (no restoration needed). All plan tasks complete; serving models unchanged.
