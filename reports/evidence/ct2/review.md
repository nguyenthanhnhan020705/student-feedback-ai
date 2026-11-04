# Independent CT2 review and resolution

Reviewer: ct2_review, fresh-context read-only agent. Scope: CT2 runner, tests,
plan, report and evidence only; no edits, no reviewer subagents.

Original verdict: With fixes. Critical: none. Important: one. Minor: none.

Important: select_candidate compared F1 against a moving current winner.
Baseline F1 .7500000/Accuracy .90, sqrt_balanced .7499992/.91,
balanced .7499984/.92 incorrectly selected balanced, outside the tolerance
band of the maximum F1. Reviewer reproduced this; executor independently did too.

Fix: establish a global best F1, take its 1e-6 band, then a global best
Accuracy within that band, take its 1e-6 band, then baseline/fixed order.
review-red.txt reproduces the bug with an assertion failure; review-green.txt
shows 37 passed (24 CT2 + 13 CT1). No independent second review is claimed.

Reviewer independently checked all 19 run-1 payload hashes, all four evidence
copies, report metrics, per-class losses and regression counts. Source protections,
train-only fitting, null handling and honest scientific limits were confirmed.

Final run-2 binds fixed source; replay-2.txt verifies six reloaded candidates,
selection and combined result. run-comparison.txt confirms that every candidate
evaluation and the combined metrics/regressions are identical to run-1.
Run-1 and its original runner are preserved as review history.

Behaviors set aside and executor decisions:

- Unrelated dirty integration changes: preserve them; this review certifies CT2 only.
- API/UI after research promotion: no promotion in CT2; preserve serving baseline.
- Independent generalization/human correctness of known-case labels: unavailable;
  retain development-only conclusions and provisional-label caveat.
- Deliberately coordinated replacement of artifacts and checksum receipts: local
  replay provides consistency, not an external trust anchor. Existing trusted-team
  artifact scope stands; no extra publication/security claim or new workflow.

Closing full-suite and CT1 preservation evidence is recorded in README.md and
the CT2 ledger. These are execution checks, not a new reviewer verdict.
