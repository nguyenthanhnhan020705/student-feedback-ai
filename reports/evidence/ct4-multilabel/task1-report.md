# Task 1 implementation report

Implemented an isolated `demo_v3` application with API `/api/v3/predict`, contract `3.0`, launch target `demo_v3.main:app` on port 8002. Existing applications, corpora, models, research runners, receipts, and documents were not edited. No Git mutation, fitting, external service, or dependency installation was performed. The parent owns the preexisting-file inventory, full-suite verification, historical no-fit replays, live server, independent final review, and finite exploratory evaluation.

## Behavior and decisions

- Pure aggregation exhaustively tests all 32 combinations of two polarity booleans and eight core topic sets, including deduplication and invalid evidence. Positive AND negative yields `mixed` (displayed **Trung tính**); neither yields `undetermined` (**Chưa xác định**). At least two distinct core groups yield `education_quality`; no group yields `other_domain` (**Lĩnh vực khác**).
- Bounded rules inspect asserted fragments, mask paired quotations before segmentation, exclude explicit vocabulary/name complements, preserve raw offsets, deduplicate referents, and handle local evaluative negation. Coordinating `và` splits only after a predicate and before an explicit core subject; coordinated teacher referents remain one group. Raw accent constraints distinguish `có`/`cô` and `bạn`/`bàn`/`bẩn` before detector-only accent folding. No whole-sentence special cases, top-two score rules, or old-neutral mapping exist.
- CT4/CT5 provenance and runtime loading reuse the existing `DemoService` read-only. **CT4 is an audit-only analysis component:** each raw clause receives actual CT4 inference; disagreements cannot add, remove, or veto evidence. This is an implementer-selected bounded experiment, not a learned multilabel model or an independently proven algorithm. Internal clause audit is returned by `Service.analyze`; the public response exposes only the version and final two labels.
- Invalid raw types, blank input, extra fields, lone surrogates, invalid JSON/UTF-8, or more than 5000 raw codepoints return 422. Missing, malformed, or checksum-mismatched rules/model/provenance/runtime leave a startable server with readiness false and prediction 503. CT4 inference exceptions and invalid service outputs return 500 without business fallback or partial labels.
- UI centralizes the exact four/five Vietnamese labels, accepts only strict own response properties with version 3.0 and known primitive string codes, rejects prototype labels/inherited properties, uses a Promise race for a 10-second whole-body deadline, prevents duplicate submission, and uses a monotonic input revision to reject stale results even after edit-away/edit-back. Input is preserved during errors, and connection/retry flows recover. No confidence percentages are displayed.

Ruling: use the already selected linked worktree and the parent-owned plan/ledger and preservation inventory; do not run skill helper scripts that create another workspace or mutate Git. The explicit task scope requires preserving all preexisting files and prohibits those mutations.

Ruling: run the complete new scoped suite here; the parent runs the complete existing real-data/browser suite once after the core freeze. This avoids duplicate expensive regression runs and avoids simultaneous writes to historical browser evidence. Scoped success is not a claim that the full old suite passed.

## Actual RED and GREEN evidence

All commands ran from the existing `integration-p0` worktree using its locked `.venv`. Each pytest command used `-B` and `-o cache_dir=reports/evidence/ct4-multilabel/cache-task1`; logs are new files under this evidence directory.

| Log | Command suffix after `./.venv/Scripts/python.exe -B -m pytest` | Observed result |
| --- | --- | --- |
| `engine-red.txt` | `tests/test_demo_v3.py -q` | 78 failed; missing evidence engine asserted inside tests; exit 1 |
| `engine-green.txt` | `tests/test_demo_v3.py -q` | 78 passed; exit 0 |
| `api-context-red.txt` | `tests/test_demo_v3.py tests/test_demo_v3_api.py -q` | 37 failed, 78 passed, 5 errors; missing service/API plus context tests. Two errors also exposed excessively long pytest parameter IDs on Windows; IDs were shortened before rerun. Exit 1 |
| `api-context-red-clean.txt` | `tests/test_demo_v3.py tests/test_demo_v3_api.py -q --tb=short` | 41 failed, 78 passed, 3 expected missing-service fixture errors; exit 1 |
| `api-context-green.txt` | `tests/test_demo_v3.py tests/test_demo_v3_api.py -q --tb=short` | 122 passed, one existing warning; exit 0 |
| `accent-red.txt` | `tests/test_demo_v3.py -q -k accented_have --tb=short` | 6 failed, 83 deselected; exit 1 |
| `pronoun-red.txt` | `tests/test_demo_v3.py -q -k accented_pronouns --tb=short` | 3 failed, 89 deselected; exit 1 |
| `accent-green.txt` | `tests/test_demo_v3.py tests/test_demo_v3_api.py -q --tb=short` | 131 passed, one existing warning; exit 0 |
| `browser-red.txt` | `tests/frontend/test_demo_v3_ui.py -q -k actual_labels --maxfail=1 --tb=short` | Expected HTTP 500 from missing frontend, fixture assertion failed; exit 1 |
| `task1-green.txt` | `tests/test_demo_v3.py tests/test_demo_v3_api.py tests/frontend/test_demo_v3_ui.py -q --tb=short` | **173 passed, one existing warning, 56.84 seconds; exit 0** |

The final scoped run covers 131 engine/API tests and 42 real Chrome/Edge browser tests. Six actual inference cases per browser have separate JSON/PNG artifacts under `browser/`, explicitly marked `fixture=false`. Error, malformed-response, timeout, and stale-request tests use controlled fixtures and are not represented as real model quality evidence. The desktop Chrome mixed/multiple-topic screenshot was visually inspected. The existing warning concerns Starlette's use of httpx in TestClient; no dependency was changed.

## Freeze and limits

`core-freeze.json` was created before the parent authored finite exploratory variants. It records all six v3 root source/config files plus thirteen reused source/artifact checksums. Rules are versioned `experimental-1.0.0`, provenance is assistant-authored and specification-exposed, and a pinned SHA-256 is enforced by the detector. `task1-verification.json` records final source hashes and confirms that core files still match that freeze. Browser assets/tests were finalized before the completed scoped run.

The passing handoff examples are specification tests, not independent validation. Vocabulary is bounded; unseen predicates, implicit subjects/aspects, indirect reported speech, sarcasm, questions/modality, long/double negation, and ambiguous accentless text remain quality risks. Local predicate inversion does not solve Vietnamese negation generally. Quotation/name guards are explicit heuristics and can suppress genuine content; segmentation does not perform full syntax or coreference analysis. Outside-group content alone cannot create a second core topic, but lexical ambiguity can still misidentify a referent. Errors on future variants must remain visible, without tuning this freeze to their expected labels. No comparison to old UIT-VSFC accuracy is valid across the changed ontology.

Task 1 status: scoped engineering complete; `engineering_complete_independent_evaluation_pending`. Parent integration/final review obligations remain separate.

## Independent-review fix revision

Addressed confirmed R1–R3 from `review.md` in one bounded fix wave. Only production file `demo_v3/detector.py` and regression file `tests/test_demo_v3.py` changed. No topic/polarity lexicon or `rules.json` changes were made, and the four finite exploratory errors were not used for tuning.

- R1 root cause: quote patterns excluded line breaks, so accepted multiline quoted examples reached segmentation. Supported straight/typographic paired quotations now mask across newlines with exactly the same raw length.
- R2 root cause: mention guards ran after contrast/coordinating segmentation, which dropped their governing context. Explicit vocabulary/name complements now mask before boundary selection. Hard punctuation or explicit reporting/definition completion ends their bounded scope, preserving subsequent independent assertions. Raw-to-folded index mapping preserves NFC/NFD source offsets. This remains a bounded complement heuristic; unmarked indirect speech and ambiguous completion remain limitations.
- R3 root cause: every folded `tu` truncated all following content. Bare word-marker uses now require an explicit lexical governing context or a definition context. Source prepositions such as `từ trường` and `từ phòng học` preserve their following evidence, including sentence-initial source phrases. Existing quotation and vocabulary regression cases still pass.

Added 26 regressions across NFC/NFD, four paired-quote styles, both reported false-evidence cases, later real assertions after mentions, and ordinary source prepositions. Command `./.venv/Scripts/python.exe -B -m pytest tests/test_demo_v3.py -q -k review_r --tb=short -o cache_dir=reports/evidence/ct4-multilabel/cache-review-fix` produced **22 failed, 4 passed, 92 deselected**, exit 1 (`review-red.txt`), before production changes. The whole engine then passed 118 tests (`review-engine-green.txt`).

Final scoped command `./.venv/Scripts/python.exe -B -m pytest tests/test_demo_v3.py tests/test_demo_v3_api.py tests/frontend/test_demo_v3_ui.py -q --tb=short -o cache_dir=reports/evidence/ct4-multilabel/cache-review-fix` produced **199 passed, one existing warning, 71.49 seconds**, exit 0 (`review-green.txt`): 157 engine/API and 42 Chrome/Edge tests. No full-old-suite result is claimed by this fix report; the parent owns the rerun and live-server refresh.

`review-fix-verification.json` records the new revision source hashes, the exact two changed source files, unchanged rules and all thirteen reused frozen source/artifact hashes, and explicit links/checksums for the preserved original `core-freeze.json` and `task1-verification.json`. `review-fix.diff` contains the production/test delta from that original snapshot; the before-detector backup was verified against the original freeze. Original exploratory-case inputs, outputs/evaluation, freeze, and task1 receipt remain historical evidence, not revised claims for this code. This fix revision has regression verification and no fresh holdout evaluation. A parent-requested scoped re-review and final integration checks remain pending.

## R4 correction after the scoped re-review

The requested single scoped re-review confirmed R1–R3 and identified a local regression in the changed bare-word-marker logic: an explicit statement that a word occurs on a board/page lacked the definition context required by the new guard. This could manufacture sentiment from `Từ tốt và tệ xuất hiện trên trang.` or `Từ tốt xuất hiện trên bảng.`. This is a regression within the previous change, not a request to extend the sentiment/topic vocabulary or tune the exploratory errors.

Added ten focused NFC/NFD checks: the two reported occurrence statements, a later independent classroom assertion, and both ordinary source-preposition controls. The focused command `./.venv/Scripts/python.exe -B -m pytest tests/test_demo_v3.py -q -k review_r4 --tb=short -o cache_dir=reports/evidence/ct4-multilabel/cache-review-r4` produced **6 failed, 4 passed, 118 deselected**, exit 1, before production changes (`review-r4-red.txt`). The correction adds explicit occurrence/reporting-on-board/page context beside the existing sentence-initial definition context; it does not restore unconditional suppression for `từ`.

Final scoped command `./.venv/Scripts/python.exe -B -m pytest tests/test_demo_v3.py tests/test_demo_v3_api.py -q --tb=short -o cache_dir=reports/evidence/ct4-multilabel/cache-review-r4` produced **167 passed, one existing warning, 14.12 seconds**, exit 0 (`review-r4-green.txt`). All original tests and the previous 26 regressions remain present. The frontend did not change; browser tests were not repeated in this scoped command. The prior 42 Chrome/Edge passes remain recorded in `review-green.txt`, and the parent owns the complete final-state suite.

Only `demo_v3/detector.py` and `tests/test_demo_v3.py` changed again. `review-r4-verification.json` records final hashes, links to both previous-revision and original receipts, unchanged rules and reused frozen sources, and the actual verification scope. `review-r4.diff` is the correction against verified snapshots from the prior revision. No earlier freeze, evaluation, receipt or exploratory input/output was overwritten. Existing full-suite-final runs are superseded by this production change; the parent reruns the final suite on the stable source. No additional independent review round or fresh independent semantic-evaluation result is claimed.
