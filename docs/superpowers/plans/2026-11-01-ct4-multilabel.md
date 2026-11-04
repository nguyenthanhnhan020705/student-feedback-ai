# CT4 multilabel demo Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. User scope overrides commit/cleanup defaults.
**Goal:** Implement and verify an isolated experimental v3 following the settled business ontology.
**Architecture:** Bounded evidence detector + pure aggregator, frozen CT4 clause audit, isolated versioned API/UI.
**Tech Stack:** Existing Python/FastAPI/scikit-learn/vanilla JS/pytest/Playwright only.
**Spec:** docs/quality/ct4-multilabel-agent-handoff.md and docs/superpowers/specs/2026-11-01-ct4-multilabel-design.md.
## Global Constraints
Preserve all originals, models and CT1?CT5. No fitting, new dependency, external API, Git mutation or publication. Mixed iff positive AND negative evidence; information-only -> undetermined. At least two distinct core topics -> education_quality; zero -> other_domain. Exact Vietnamese labels per handoff. No hardcoded sentences/top2/old neutral mapping. Strict raw input max5000 codepoints. Errors422/503/500 remain errors.
## Review Focus
- Negated or quoted vocabulary must not silently create false mixed or topic evidence.
- Repeated/coordinated lecturer referents must deduplicate; outside-group content alone cannot create a second core topic.
- Missing or malformed rules/provenance/runtime must fail readiness, not startup or business fallback.
- Out-of-order requests and edit-away/edit-back cannot display a result for an obsolete request.
- Unsupported input semantics must remain visible as limitations and exploratory errors, not mislabeled independent validation.
## Task 1: New engine, API and UI
Files: only demo_v3/, tests/test_demo_v3*.py, tests/frontend/test_demo_v3_ui.py; evidence under reports/evidence/ct4-multilabel/.
Interface: aggregate(positive:bool, negative:bool, topics: iterable[str])->dict(sentiment,topic); Detector/Service deliver valid contract3.0 with internal audit kept separate.
- [x] Write exhaustive aggregator + detector tests before code; run missing-feature RED then GREEN.
- [x] Write API tests before code for raw boundary/types/JSON/Unicode, frozen readiness and inference exceptions; run RED then GREEN.
- [x] Write browser tests before frontend for actual labels, strict response validation, timeout/duplicate/stale/recovery; RED then GREEN Chrome/Edge.
- [x] Freeze experimental rules/config, record provenance and limitations, self-review, hand off scoped test logs.
## Task 2: Finite verification and integration review
- [x] Author bounded assistant_proposed variants after config freeze; no tuning to evaluation outcomes. Save actual outputs, detector errors, confusion/per-class/support/joint under new ontology.
- [x] Run full suite with TV2_RUN_REAL_DATA=1 and pip check.
- [x] Fresh no-fit replay CT1?CT5; preserve all source and artifact bytes and restored old browser evidence.
- [x] Independent final review; regression RED/GREEN for blocking findings and fresh full suite if production changes.
- [x] Start live v3 on8002, check health/API/assets and Chrome/Edge screenshots; report limitations and independent_evaluation_pending.
