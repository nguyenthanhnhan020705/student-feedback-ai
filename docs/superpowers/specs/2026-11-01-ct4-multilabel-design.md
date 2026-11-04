# CT4 multilabel trial design ? 2026-11-01
Authority: docs/quality/ct4-multilabel-agent-handoff.md, especially sections 1, 2, 8.
The user authorized implementation and delegated minor technical choices. Business ontology is settled; the experimental detector choice below is implementer-selected, not user-approved algorithm research.

## Approach and alternatives
Use an isolated demo_v3 application, API /api/v3/predict, contract_version 3.0, port 8002. No changes to any existing application, model, corpus, research runner or receipt. Reuse read-only DemoService provenance/runtime/model validation and CT4 inference for clause-level analysis. A versioned, bounded experimental evidence detector handles explicit referents, evaluative predicates, contrast/coordinating punctuation and local negation contexts; CT4 predictions corroborate or audit local fragments but never create mixed from old neutral or top-two scores. No external service, dependencies or training.
Renaming old labels cannot establish this ontology. A learned multilabel/aspect detector would need independently labeled data and separately authorized training, so is deferred. Broad arbitrary keyword co-occurrence is insufficient: detector must attach evaluative expressions to asserted clauses and exclude quoted/metalinguistic and locally negated evidence where supported. Unsupported semantics remain documented quality errors, never technical success claims.

## Components
- demo_v3/ontology.py: pure validated aggregation of positive/negative booleans and deduplicated core topic set. Four and eight exhaustive combinations.
- demo_v3/detector.py plus rules.json: explicit bounded context-aware evidence extraction, canonical normalized/accent-folded matching only in new detector, clause offsets/audit internally. Do not split every 'va'; coordinated lecturer referents deduplicate. Evaluate whole context as needed. Information-only statements cannot receive positive/negative from CT4 alone.
- demo_v3/service.py: frozen CT4+CT5 read-only readiness via existing service, no-fit inference on detected clauses with errors propagated; experimental rules validation/readiness, aggregate evidence independent by task. No silent exception fallback.
- demo_v3/main.py: strict input 1?5000 Unicode codepoints, no surrogate/extra field, 422/503/500, schema enum validation. Technical faults never converted to undetermined/other_domain.
- demo_v3/frontend/: exact Vietnamese labels, raw input, full-body timeout, own-property/strict string/version validation, duplicate prevention, stale result guard including edits away and back.

## Evaluation
Known handoff matrix is specification, not holdout. Freeze configuration before a finite set of assistant_proposed variants is evaluated; report support, confusion/per-class and joint exact match on that exploratory set only. Aggregator correctness is distinct from detector accuracy. No ontology comparison to old UIT-VSFC metrics. Status engineering_complete_independent_evaluation_pending until independent human-reviewed data exists. Explicit limitations: negation scope, reported speech, sarcasm, implicit aspects, ambiguous accentless text, outside domain.

## Preservation and operations
Initial inventory and exact JSON/PNG evidence backup precede new files. Existing linked worktree is retained; no reset/clean/branch change/commit/push/merge/publication. Full real-data/browser regression, pip check, fresh no-fit CT1?CT5 replay, byte-preservation audit and independent review. Any refreshed old screenshots copied to new evidence before restoring only verified backup bytes. Start new local server 8002 and verify live API/UI. Phase6/P1 excluded.
