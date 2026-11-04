# Independent CT1 review

Reviewer: ct1_review, fresh-context read-only agent. Scope only CT1 files and
evidence, not unrelated pre-existing integration changes. No reviewer edits.

- Critical: none.
- Important: evaluate constructed case rows by len(cases), silently dropping
  extra model predictions. Missing predictions raised IndexError instead of
  validation error. Fixed by validating every raw task's case output length
  and canonical labels before row construction.
- Minor: none.
- Reviewer independently checked all 49 inventory hashes in live/snapshot,
  receipt hashes, canonical order, null denominators and honest limitations.
- Condition for readiness: fix alignment issue and complete tests/replay.

Condition satisfied: regression tests first failed for both extra and missing
outputs; final suite 38 passed, no skips. Final baseline-v2 snapshot replay
passed, original artifacts unchanged. Original candidate snapshot preserved;
v2 is authoritative. No additional review cycle or unrelated changes.
