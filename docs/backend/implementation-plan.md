# TV5 Backend P0 implementation plan

Goal: complete the independently testable Backend against approved API/environment v1.0.
Architecture: retain FastAPI routes and ModelService; pass raw input to trusted pipelines. Fixture artifacts live only in temporary test directories. Real M2-S/M2-T integration remains pending.

- [x] Verify existing baseline in an isolated Backend environment (9 passed).
- [x] Add contract tests for success, strict types, Unicode limits, invalid outputs and internal errors; observe failures before fixes (5 failures reproduced).
- [x] Add loader tests using serialized sklearn fixtures: metadata, checksum, compatibility, missing/invalid artifacts, reload and output validation.
- [x] Fix contract gaps and serve the existing frontend at the same origin, keeping API 404/405 behavior.
- [x] Run full suite, record environment/logs and update Backend handoff (57 passed, 1 upstream deprecation warning; pip check clean).

Constraints: Python 3.13; sklearn 1.6.1; API contract 1.0; no P1 endpoints or changes to TV2–TV4 code or root dependencies. Existing specification determines the design; no additional product scope.
