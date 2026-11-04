# Independent whole-change review — 2026-11-01

Verdict: **changes requested** for three bounded detector-context defects below. The isolated architecture, aggregation, API and UI are otherwise consistent with the reviewed requirements. Passing engineering tests and specification examples do not establish general detector quality.

Authority: handoff sections 1, 2 and 8; the 2026-11-01 design and implementation plan. The plan's Review Focus was applied to negated/quoted evidence, deduplicated topics, readiness, obsolete UI requests, and truthful evaluation claims. Review scope is the new v3 files and tests in `review-package.diff`; originals are read-only.

## Findings

### R1 — P2, fix before technical acceptance: paired quotations leak across newlines

Location: `demo_v3/detector.py:101` (`_mask_quotes`, regex on line 102).

The quote matcher explicitly excludes newlines. A paired, multiline quotation is therefore left unmasked and the newline segmentation turns its contents into asserted evidence. This is ordinary multiline text accepted by the textarea and API, not an unmatched quotation or sophisticated reported-speech case.

Read-only probe, with an actual newline inside the quotes:

```text
"Giảng viên tốt
phòng học nóng" là câu ví dụ.
```

Actual: `mixed / education_quality`. Expected under the existing quotation policy: `undetermined / other_domain`. Both displayed labels are manufactured entirely from a quoted example. Preserve paired-quotation masking across accepted line breaks before segmentation, with a regression covering straight and supported typographic quotes. Preserve offsets.

### R2 — P2, fix before technical acceptance: segmentation loses metalinguistic scope

Locations: `demo_v3/detector.py:139`, `:147`, `:162`; mention suppression at `:110` and `:114`.

The detector splits contrasts and coordinating subjects before identifying a metalinguistic complement. A word inside that complement can trigger a split; only the first resulting fragment retains the marker. Later fragments incorrectly become asserted predicates and core topics.

Read-only probes:

| Input | Actual | Expected interpretation |
| --- | --- | --- |
| `Giảng viên viết cụm từ tốt và phòng học nóng trên bảng.` | `negative / education_quality` | `undetermined / lecturer`; the facility and heat are words written on the board |
| `Cụm từ tốt nhưng tệ xuất hiện trên trang.` | `negative / other_domain` | `undetermined / other_domain`; this is a phrase mention |

This defeats the explicitly implemented unquoted vocabulary/name guard and the plan's requirement that quoted/metalinguistic vocabulary not create evidence. Establish the bounded mention context before choosing boundaries, or carry its scope into the resulting fragments. Avoid solving this by suppressing every subsequent independent assertion. Add regressions for a genuine assertion after a mention as well as these false-evidence examples.

### R3 — P2, fix before technical acceptance: every ordinary `từ` discards remaining evidence

Location: `demo_v3/detector.py:114` and `:117`.

The expression `(?:cum )?tu` treats every occurrence of `từ` as a vocabulary marker, regardless of its grammatical role. It truncates the rest of both topic and polarity text, deleting otherwise supported explicit evidence.

Read-only probes:

| Input | Actual | Expected interpretation |
| --- | --- | --- |
| `Giảng viên từ trường khác đến và dạy tốt.` | `undetermined / lecturer` | `positive / lecturer` |
| `Giảng viên nhiệt tình và từ phòng học phát ra tiếng ồn.` | `positive / lecturer` | `positive / education_quality`; at least the explicit classroom referent must survive |

Use a bounded contextual vocabulary-marker rule that distinguishes a source preposition from an explicit word/phrase mention. This does not require comprehensive Vietnamese parsing. Preserve the current metalinguistic regression cases while adding ordinary-preposition cases.

## Additional quality limits, not new algorithm-expansion requests

The saved exploratory errors are candidly retained: variants 02, 17, 30 and 31. In particular, `Cô không giảng khó hiểu.` is classified negative, and `Không nhận xét về giảng viên.` still adds lecturer. A review probe also returned `positive / education_quality` for `Tôi không nói về phòng học; thầy giảng dễ hiểu.` because the nonassertion guard is anchored at the start of a clause. These show that suppression and local negation remain narrow; do not claim comprehensive negation handling. They are not evidence for silently expanding this task into new training or a general semantic parser.

## Verified strengths and evidence

- Read all 13 source/test files represented by the review package, the binding requirements, task report, verification receipt, freeze, exploratory output and evaluation runner, plus reused `demo_v2/service.py`.
- Recomputed SHA-256 values in a read-only Python process: all six `core_sha256` entries, all thirteen reused source/artifact entries, and all thirteen task1 source/test hashes matched their saved receipts at review time.
- Pure aggregation follows the complete boolean truth table and deduplicated core-topic cardinalities. No old-neutral conversion, top-two evidence, sentence equality special case, or exception-to-business-label fallback was found.
- Repeated teachers deduplicate; the review probe `Thầy và cô đều giảng dễ hiểu.` returned `positive / lecturer`. The supported prefix case `Không bàn về phòng học; thầy giảng dễ hiểu.` also returned `positive / lecturer`.
- Service keeps CT4 clause inference audit-only. Its readiness includes the versioned/checksummed rules and reused frozen CT4/CT5 provenance/runtime checks. Initialization failures leave the API startable; inference exceptions reach 500 handling.
- API uses strict strings, raw 5000-codepoint validation, blank/surrogate rejection, forbidden extras, version 3.0 and response enums. Invalid request, readiness and inference paths remain 422, 503 and 500 respectively.
- UI maps exactly the four sentiment and five topic labels, validates own properties/primitive strings/version, covers the whole response body with its timeout, prevents simultaneous submissions, and uses a monotonically increasing text revision to reject stale results including edits away and back. No calibrated-confidence claim is shown.
- `task1-green.txt` records 173 passed and one warning, including 42 Chrome/Edge tests. Browser fixture cases are identified separately from actual model cases. This review inspected those tests and the receipt, and did not rerun them.
- Saved evaluation separates specification 15/15 from assistant-proposed exploratory 32/36 joint exact match, with confusion matrices, per-class support and four retained errors. It labels the new ontology, no-fit execution, CT4 audit role and lack of independent human review correctly. Those values apply to the recorded original freeze only.
- `historical-replay.json` records zero exits for five no-fit historical replays. `preservation.json` records 708/708 matching original hashes before the parent's full run. These are inspected parent evidence, not independently rerun historical evaluations.

## Review method and boundaries

Executed only short read-only `Detector.detect`/`aggregate` probes and hash checks with the existing Python environment and `-B`; no fit, dependency installation, historical runner, browser evidence refresh, source edit or Git mutation. An initial PowerShell pipeline incorrectly replaced Vietnamese characters during transport; those garbled outputs were discarded. Every probe reported above was rerun with explicit UTF-8 transport and verified text.

Only this new review report was written. The parent owns the running full real-data suite, final pip check, post-suite preservation, live server checks and any corrective work. This review does not certify their eventual completion or production readiness. It does not certify independent semantic accuracy, general negation/reported-speech coverage, an accuracy improvement over the old ontology, or a final human-reviewed dataset. This is an independent code-review role, not independent human labeling of evaluation data.

Fix R1–R3 with focused RED/GREEN regressions and rerun affected checks before claiming technical acceptance. If core changes, retain the original freeze and exploratory evaluation as historical evidence; record the new source hashes and distinguish regression verification from fresh holdout evaluation. The appropriate eventual status remains `engineering_complete_independent_evaluation_pending`, provided the remaining integration checks pass.
