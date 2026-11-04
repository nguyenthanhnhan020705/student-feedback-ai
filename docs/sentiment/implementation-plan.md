# TV3 completion plan ? 2026-10-28

Scope: implement the approved Phase 0 data/model contract and Phase 3 Sentiment checklist. Work locally beside uncommitted TV2 changes; only Sentiment-owned files are changed.

- [x] Recover the existing TV3 baseline from feature/sentiment-model into empty Sentiment scaffolds.
- [x] Verify fixture tests with the current local Data interface in an isolated Python environment.
- [x] Add tests for train-only vocabulary, evaluation without fitting, tie breaking and the complete train/evaluate CLI artifact lifecycle.
- [x] Correct defects demonstrated by those tests.
- [x] Add a reproducible notebook and handoff/report with exact commands and limitations.
- [x] Run the focused suite and Data regression tests, save logs and environment versions.

User confirmed TV2 completion and authorized continuation on 2026-10-28. Use local Data for real training; record unchanged pending_leader_review manifest status and the local dependency snapshot as handoff limitations. Do not treat it as a leader-approved environment lock.

Verification: 45 passed, no skipped tests; real Data tests enabled. Actual training and reload evidence saved. Independent review found and verified invalid-label rejection and Unicode repairs. All changes local; no commit, push or merge.
