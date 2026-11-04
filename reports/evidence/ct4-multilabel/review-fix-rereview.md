# Scoped fix re-review — 2026-11-01

Verdict: **R1 ADDRESSED; R2 ADDRESSED; R3 ADDRESSED for the reported source-preposition defect. Changes requested for one new P2 regression introduced by the fix, R4 below.**

This is exactly one scoped re-review of `review-fix.diff`, the associated verification receipt, appended task report and original review. It does not reopen the original exploratory evaluation or expand the detector's research scope.

## Original findings

| Finding | Verdict | Evidence |
| --- | --- | --- |
| R1: multiline paired quotations | ADDRESSED | Supported quote patterns now include line breaks and preserve raw length. Original quoted-example probe returns `undetermined / other_domain` in NFC and NFD. Added tests cover all four supported quote pairs and both normalization forms. |
| R2: metalinguistic scope lost at segmentation | ADDRESSED | Mention masking now precedes segmentation. Both original false-evidence probes return their expected labels in NFC/NFD. Reporting completion and punctuation release later real assertions; `Giảng viên viết cụm từ tốt và tệ trên bảng nhưng phòng học nóng.` retains `negative / education_quality`. |
| R3: ordinary source `từ` truncates valid evidence | ADDRESSED | Both original source-preposition probes now retain their polarity/topic evidence in NFC/NFD. The changes introduce contextual word-marker recognition rather than deleting all following content at every occurrence. This is bounded recognition, not complete disambiguation of every use of `từ`. |

## R4 — P2, fix before technical acceptance: ordinary word-occurrence statements now create sentiment

Locations: `demo_v3/detector.py:132` and `:156`.

The new bare-`tu` matcher recognizes a governing lexical verb or a sentence-initial definition. It does not recognize an explicit statement that a word occurs on a page/board. At the same time, `_evidence` now bypasses the original sentence-initial `tu` nonassertion guard unconditionally. Therefore a previously suppressed, plainly metalinguistic statement creates sentiment evidence:

| Input | Original freeze | Fix revision | Expected |
| --- | --- | --- | --- |
| `Từ tốt và tệ xuất hiện trên trang.` | `undetermined / other_domain` | `mixed / other_domain` | `undetermined / other_domain` |
| `Từ tốt xuất hiện trên bảng.` | `undetermined / other_domain` | `positive / other_domain` | `undetermined / other_domain` |

Both revised outputs were reproduced in NFC and NFD. Original outputs were independently reproduced by loading the original detector source from the existing review package in memory, with the unchanged rules. No original source file was written or replaced.

This is a new regression within the changed word-marker logic, not an unseen-predicate request or an attempt to tune the four exploratory errors. Extend the bounded recognition to explicit word-occurrence context while keeping ordinary source prepositions and later independent assertions visible. Add a regression pairing this context with the R3 source examples. A broad restoration of every-`từ` truncation would reintroduce R3.

## Verification and boundaries

- Read the complete fix diff and the 26 added regression cases. Only detector production code and its engine tests changed in the recorded source set.
- Recomputed all thirteen revision source/test hashes: they match `review-fix-verification.json`. All thirteen reused source/artifact hashes still match the original freeze. The recorded checksums of the original freeze and task1 receipt also match. `rules.json` is unchanged.
- Inspected actual log tails: focused RED is 22 failed, 4 passed, 92 deselected; scoped GREEN is 199 passed, one warning, 71.49 seconds. These are recorded runs, not a suite rerun by this reviewer.
- Executed only short read-only detector/aggregator probes, UTF-8 input transport, in-memory original-code comparison and hash checks using the existing Python environment with `-B`.
- No browser/history/full-suite rerun, fitting, dependency change, source edit, exploratory-case change, old evidence refresh or subagent. Only this new re-review report was written.
- General negation, ambiguous complements, implicit aspects and indirect reported speech remain existing documented quality boundaries. For example, lexical-governor recognition still does not resolve every source use following verbs. This review does not claim comprehensive semantic coverage or request that expansion.
- Original evaluation remains evidence for the original freeze only. The parent owns final-state evaluation provenance, full suite, live restart, preservation and any corrective action. No independent semantic accuracy, human-reviewed dataset or production readiness is certified here.

R1–R3's original reproducers are resolved, but the fix revision should not receive an unconditional technical-acceptance verdict while R4 produces false mixed evidence from an explicit word-occurrence statement.


## Parent correction record after this scoped review

The independent verdict above describes the reviewed intermediate revision and is retained verbatim. R4 was subsequently reproduced with six failing/four passing focused regressions, then fixed; all167 engine/API tests passed with one existing warning in14.12s. See review-r4-red.txt, review-r4-green.txt, review-r4-verification.json and review-r4.diff. Rules/lexicon/frontend/reused controls unchanged. The live final server also passes all four original R1?R4 reproducer HTTP checks; see live-demo.json review_samples. No third independent review is claimed. Final full regression and preservation remain parent-owned closing checks, separately recorded in handoff-verification.json when successful.
