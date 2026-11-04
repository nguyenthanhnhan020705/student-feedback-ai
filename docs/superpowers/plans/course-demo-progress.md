# SDD ledger — plan: docs/superpowers/plans/2026-10-30-course-demo-completion.md

Leader approved six-phase plan in conversation 2026-10-30; current execution starts with Phase 1. Data/API acquisition authorized if needed. No publication, push, merge or P1 authorization inferred.

## Phase 1 — complete

- BASE: feature/integration-p0 at 0ebd066, existing uncommitted integration work preserved.
- Git fetch succeeded. Root TV2–TV4 files in ml/notebooks/models/data match integration byte-for-byte.
- TV5 source 666d3b7 plus local edits; integration model_service.py differs due to previously added metadata validation. No new source copied over it.
- TV6 source feature/frontend-dashboard; four frontend file differences are missing final newline in integration, no behavior changes.
- Inventory records actual commits/status/hashes in reports/evidence/phase-6/source-inventory.json.
- Ruling: retain existing isolated worktree, no new checkout — already linked and outside main/develop.
- Ruling: configuration/docs verification uses actual fresh install and startup, no synthetic implementation tests — Phase 1 does not change app behavior.
- Ruling: add nbformat with its transitive dependencies to lock — required by environment v1.0, missing in previous merged freezes; keep all existing versions fixed.
- Ruling: use persistent repo ledger rather than Bash-only skill helper (Bash unavailable); no changes to protected .git.
- Pre-flight: Phase 2 consumes locks/artifacts from Phase 1; Phase 3 consumes verified ML; Phase 4 consumes API; Phase 5 verifies combined app; Phase 6 uses real evidence. No interface changes planned.
- Known pending bugs: invalid UTF8 JSON envelope; UI prototype labels; response-body timeout. Historical failing evidence remains valid and is not marked green.
- Notebook kernel execution tooling will be verified in Phase 2 separately; runtime includes nbformat for validation.

### Verification / handoff

- Fresh venv `.local-tools/phase1-verify`: installation exit 0; added nbformat 5.11.1 and dependencies, original ML versions unchanged. Full exact freeze written to runtime lock, browser superset synchronized. Reinstall from final lock with --no-index succeeded.
- `pip check`: No broken requirements found.
- `reports/verify_phase1.py`: imports, five metadata versions and both artifact SHA256 pass. HTTP server from external cwd serves health and all four UI assets with real models (ready=true) and empty model directory (ready=false).
- Fresh-env pytest: `tests/test_health.py tests/integration/test_prediction_flow.py -q`: 13 passed, 1 Starlette/httpx deprecation warning in 13.76s. This is targeted verification, not full suite acceptance.
- Evidence: reports/evidence/phase-1/{fresh-install,locked-install,pip-check,pytest-clean-env}.txt, environment-startup.json and server logs.
- Updated docs/development.md with commands actually exercised, dependency separation, missing-model behavior, local artifacts and pending Phase 3–4 defects.
- No production behavior edits in this phase. No training, publication, commit, push or merge. Original member code/artifacts unchanged.
- Next: Phase 2 Data/ML verification. Phase 1 complete does not certify TV2–TV6 or entire project complete.

## Phase 2 — complete (2026-10-30)

- Scope: user requested Phase 2 only; BASE 0ebd066, existing uncommitted member/integration work retained.
- Checklist: data provenance/schema/splits; TV2–TV4 tests; configuration/selection/notebooks; fresh-process artifact reload and metrics; role reports; independent review.
- Pre-flight: Phase 1 lock/artifacts feed this verification; verified artifacts feed Phase 3. Contracts unchanged.
- Ruling: retain existing linked worktree and persistent ledger, per Phase 1; no commit/push/merge or workspace deletion during this partial-plan handoff.
- Ruling: use the Phase 1 fresh locked environment because the older integration .venv lacks nbformat. Cost: commands use the longer verification-venv path; no ML versions changed.
- Ruling: verification scripts/docs only; no production behavior changes, so existing tests plus real-data assertions are the evidence, not synthetic RED tests. Tests may fit authored fixtures; production artifacts are never retrained.
- Ruling: inspect stored notebook outputs and compare metrics; do not execute training cells or install optional interactive kernels. Cost: interactive Jupyter execution is not certified; runtime/CLI reproducibility is verified.
- Data/ML tests: 63 passed, no skips, 11 existing OptimizeWarning notices; both old integration venv and locked Phase 1 venv passed.
- Verification script initially overmatched the notebook selection summary as a metric row; exact split/algorithm token matching corrected the audit parser. No baseline evidence changed.

### Verification / handoff

- Phase 2 complete: locked command in reports/evidence/phase-2/README.md ran 63 tests, 0 skipped, 11 recorded OptimizeWarning notices (47.23s). pip check passed.
- reports/verify_phase2.py exit 0: 11426/1583/3166 source rows; 9 source files; 2 winner artifacts loaded in separate fresh interpreters; all validation/test winner metrics and authored reload samples match frozen evidence; all three configurations/notebook metric tables agree.
- Both winner vocabularies contain 13308 terms; vocabulary and IDF independently agree with train-only document frequencies. No fit on corpus was performed. 59 protected file hashes unchanged.
- Final independent review: phase2_review found no Critical/Important/Minor issues and independently reconfirmed all 59 protected hashes. See reports/evidence/phase-2/review.md.
- Final: Ruling: Backend/UI behavior and whole-project acceptance remain Phase 3–5; no app behavior changed here. Cost: existing UTF-8 JSON/prototype-label/body-timeout defects remain open, not claimed passing.
- Final: Ruling: non-winning NB/LR inference and historical training chronology cannot be freshly certified without retraining; verify frozen configurations, reports, notebook outputs, training code and train-IDF evidence instead. Cost: only winner metrics were recomputed; baseline chronology is supported by code/evidence rather than a fresh training trace.
- Final: Ruling: near-duplicate leakage and distribution rights remain unverified; normalized exact-overlap checks and local-demo authorization are the available evidence. Cost: no general leakage-free or distribution-rights claim.
- Minor (deferred): existing notebook MissingIDFieldWarning; schema/output validation currently succeeds, interactive kernel execution remains uncertified. Existing iprint OptimizeWarning is recorded rather than changing locked ML versions.
- Scoped edited-doc diff --check passed. Whole existing worktree has pre-existing whitespace at docs/roadmap/phase-0-specification.md:6 and tests/test_predict.py:87, untouched by this phase.
- Updated role reports, current integration README/roadmap and Phase 2 checklist. Original root/member workspaces preserved. No commit/push/merge. Stop here per user scope; next authorized task would be Phase 3.

## Phase 3 — complete with documented minor (2026-10-30)

- Scope: Phase 3 Backend only, BASE 0ebd066; preserve existing integration/member work.
- Checklist: reproduce invalid UTF-8; metadata regressions; real-model API and failure modes; static/cwd checks; fresh tests; independent review; evidence/docs.
- Pre-flight: verified Phase 2 artifacts feed Backend; API contract 1.0 remains unchanged for Phase 4 UI.
- Ruling: reuse linked worktree and existing ledger, as Phase 1–2; no new checkout or Bash-only helper, no commit/push/merge or cleanup of shared workspace.
- Ruling: existing UTF-8/UI failures are authorized investigation targets, not a reason to request permission again. UI fixes remain Phase 4.
- Root cause: FastAPI routing wraps UnicodeDecodeError in HTTPException(400); RequestValidationError handler never sees it.
- Metadata gaps: only four scalar metrics validated; Python major/minor string slicing accepts malformed full versions; metadata labels treated as a set despite canonical-order requirement (pipeline classes remain a set).

### Phase 3 verification / handoff

- RED: metadata + original UTF-8 test: 39 failed, 30 passed. Expanded UTF-8 variants: 3 failed, 3 routing controls passed. Failures were the intended 400/ready behavior, not environment errors.
- GREEN: locked Phase 1 Python, tests/test_backend.py tests/test_health.py tests/test_model_service.py tests/test_predict.py tests/integration/test_prediction_flow.py: 119 passed, 1 existing Starlette/httpx warning, no skips (23.28s).
- Full suite with TV2_RUN_REAL_DATA=1 and browser-enabled .venv: 196 passed, 4 failed, 12 existing warnings, no skips (129.06s). Remaining failures: test_rejects_prototype_names_as_prediction_labels and test_timeout_includes_response_body, each on chrome/msedge. Baseline was 146 passed/5 failed; UTF-8 defect now fixed.
- reports/verify_phase3.py passed: actual Uvicorn HTTP from external cwd with real and missing models; four authored sentences match direct pipelines; assets, no model-file exposure, 405 and invalid-input envelopes checked. All 59 Phase 2 protected hashes unchanged before/after. No training or artifact/metadata changes.
- pip check passed; scoped code diff --check passed (Git line-ending notices only).
- Ruling: scope metadata validation to documented schema/types/order/count coherence; no comparison of every declared hyperparameter against serialized implementation. No requirement for that comparison established; semantic authenticity is not claimed.
- Ruling: Python full stable version or standard prerelease syntax accepted within matching 3.13; package versions still exact. Pipeline classes use set comparison while metadata labels require canonical order.
- Final independent review phase3_review: no Critical/Important issues; read-only probes confirmed real readiness, HTTP mapping and metadata behavior.
- Final: minor (deferred): pre-existing lone-surrogate JSON key can produce field body instead of $body, still 422 INVALID_INPUT. Future regression must preserve the literal extra field named body. Disclosed in evidence, README and Backend report; no claim of universal envelope compliance.
- Final: Ruling: whole-project acceptance and UI defects remain Phase 4–5 per user's Phase 3-only scope; full failing suite is disclosed, no merge-ready claim or branch-finishing menu.
- Final: Ruling: training chronology/predictive quality remain Phase 2's recorded evidence, no retraining; no new quality claim.
- Final: Ruling: dataset rights unchanged (unknown), local demo only; malicious joblib inputs outside trusted team artifact contract, no untrusted-deserialization safety claim.
- Persistent ledger/worktree preserved for later phases. Integration README/development/roadmap/Backend docs updated; original root/member workspaces untouched. No commit/push/merge, no Phase 4 implementation.

## Phase 4 — complete (2026-10-31)

- Scope: Phase 4 Frontend only; BASE 0ebd066, existing uncommitted integration preserved.
- Checklist: [x] RED regressions; [x] label/timeout fixes; [x] browser behavior and real screenshots; [x] full suite; [x] independent review; [x] docs/evidence.
- Pre-flight: Phase 3 API contract 1.0 and verified artifacts feed Phase 4 UI; interface unchanged. Phase 5 consumes tested UI.
- Ruling: retain existing linked worktree and persistent ledger as earlier phases; no new checkout, commit, push, merge or cleanup. Cost: delivery remains local and uncommitted.
- Ruling: execute approved Phase 4 design directly; no new feature/design workflow. Existing UI layout will be inspected and retained if readable. Cost: no visual redesign.
- Root-cause hypotheses: truthy object indexing admits inherited prototype properties; fetch finally clears the timer before res.json and its catch swallows AbortError.
- RED: original regressions 4 failed on Chrome/Edge. Expanded Chrome checks 6 failed, 5 passed: inherited labels, coerced array labels and body-timeout recovery fail as expected; malformed JSON HTTP mapping already passes.
- Fix: require string own-property labels; keep AbortController timer through JSON reading, propagate abort/network failures and preserve HTTP error mapping for malformed JSON.
- Protected Data/ML inventory: all 59 Phase 2 hashes matched before edits.
- GREEN: complete Frontend suite 42 passed on Chrome/Edge in 103.60s; no skips/warnings. Desktop real inference screenshots refreshed; mobile MOCK screenshots visually inspected. pip check and scoped code diff --check passed.

### Phase 4 verification / handoff — complete

- Checklist complete: RED regressions; strict label/body-timeout fixes; browser behavior and real screenshots; full suite; independent review; docs/evidence.
- Full suite with TV2_RUN_REAL_DATA=1: 224 passed, 0 skipped, 12 existing warnings in 154.50s. Browser-only suite: 42 passed in 103.60s.
- Chrome 147.0.7727.101; Edge 156.0.4314.50. Actual UI/API/model prediction screenshots and JSON refreshed; mobile MOCK screenshots clearly labeled and inspected. Layout remains readable at 1280x900 and 390x844.
- Independent reviewer phase4_review found no Critical/Important/Minor issues in scoped changes. Review's pending full-suite condition satisfied by full-suite.txt.
- All 59 protected Data/ML hashes unchanged; no new training/artifact/metadata edits. pip check passed; scoped code/document diff --check passed.
- Final: Ruling: retain the pre-existing Phase 3 lone-surrogate detail-field minor outside this Frontend phase; invalid input remains rejected with 422. Cost: no universal Backend envelope-compliance claim.
- Final: Ruling: retain Phase 2 model-quality/provenance limitations; hashes are preserved, not a fresh quality or distribution-rights certification. Cost: no improved-model or rights claim.
- Final: Ruling: full regression verification does not complete Phase 5 restart/offline rehearsal, acceptance/packaging or Phase 6 reports/slides. Cost: product handoff still requires those phases.
- Persistent worktree/ledger preserved; original root/member code untouched. No commit/push/merge or Phase 5 implementation. Next task: Phase 5 when requested.

## Phase 5 — complete (2026-10-31)

- Scope: Phase 5 only; preserve integration and member work, no Phase 6 report generation.
- Checklist: [x] full suite; [x] cold start/restart/missing models/external cwd; [x] external-network-denied rehearsal with real timing; [x] local handoff and acceptance; [x] independent review.
- Pre-flight: Phase 4 API/UI and Phase 2 frozen artifacts feed operational rehearsal; Phase 6 will consume acceptance and demo evidence. Contract 1.0 unchanged.
- Ruling: reuse existing isolated worktree and persistent ledger, as Phases 1–4 — preserve uncommitted member work and reproducibility — no commit/push/merge or workspace deletion in this scoped handoff.
- Ruling: operational verification scripts and documentation use real HTTP/browser assertions, without synthetic RED tests for unchanged production behavior — Phase 5 verifies existing behavior; any production fix requires RED→GREEN.
- Ruling: deny non-loopback sockets in the rehearsal server and non-loopback browser requests, without changing host firewall/network settings — safe local verification of application dependencies — this does not certify every OS/browser background process offline.

### Phase 5 verification in progress

- Full suite: 224 passed, 0 skipped, 12 existing warnings, 177.23s; pip check passed.
- Rehearsal passed Chrome/Edge: 8 real server lifecycles, external cwd, cold/restart/missing/restored, 6 real predictions, invalid input/recovery; 59 protected hashes unchanged.
- Both network guards have negative controls; zero application external requests. Not an OS-wide/native/background socket certification.
- Added DEMO.md, demo-script.md, verifier, local packager and acceptance/evidence docs. Packaging and independent review pending.
- Ruling: retain Phase 3 lone-surrogate detail-field minor — input is rejected and local demo works — universal envelope compliance not claimed.
- Ruling: local ZIP includes dataset/artifacts, excludes venv/Python/browser/wheels — source and pinned dependencies without machine-specific executables — installation may need network; other-machine compatibility not certified.

### Phase 5 independent review and final packaging

- Independent fresh-context phase5_review: no remaining Critical/Important/Minor in Phase 5. Candidate ZIP independently checked: 252 hashes, archive integrity and all protected substantive payloads.
- Packaging receipt issue corrected: omit previous package-* receipts/logs; final sidecar authoritative. Final ZIP generation/check remains the closing verification.
- Final: Ruling: reviewer deferred OS/native/background networking and another-machine install — retain explicit application-level/Windows evidence — no broader isolation/portability claim.
- Final: Ruling: reviewer deferred training chronology, quality, near-duplicates and rights — retain Phase 2 limitations and unchanged artifacts — no new certification.
- Final: minor (deferred): pre-existing Phase 3 lone-surrogate detail field body vs $body, still 422 INVALID_INPUT; does not block demo.
- Final: Ruling: reviewer deferred Phase 6/admin/publication/Git integration — finish local Phase 5 only, retain worktree and ledger instead of branch-finishing menu/cleanup — final academic delivery still pending.


### Phase 5 completion — 2026-10-31

- Final ZIP: .local-tools/phase5-delivery/student-feedback-ai-local.zip; 2,360,983 bytes, 252 payload files independently hash-checked after creation; SHA256 c7905ea0da9f0ed77663792f92412f8c6c40b38a8f3b795544289f3a49a313fc.
- Final extracted application passed real health, all four UI assets and two-model prediction from external cwd under network guard (startup 4.337s). Child process stopped. Package sidecar records evidence; no stale package receipts/logs inside ZIP.
- Package snapshot precedes this closing receipt; final sidecar and workspace ledger are authoritative for final-package completion. Candidate remains separately preserved; final ZIP was not overwritten.
- Final integrity audit: all 252 ZIP hashes and all 59 protected Data/ML hashes match; no model training or production behavior changes.
- Full suite evidence remains 224 passed, 0 skipped, 12 known warnings. Subsequent changes only verification/packaging/documentation, so no redundant suite rerun.
- Independent review condition satisfied by final package verification. Phase 5 complete within documented limitations; Phase 6 not started. Original workspaces, branch and persistent ledger retained; no commit/push/merge/publication.
