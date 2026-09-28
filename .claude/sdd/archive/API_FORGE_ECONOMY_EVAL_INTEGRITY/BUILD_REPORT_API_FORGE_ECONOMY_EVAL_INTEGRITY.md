# BUILD REPORT: API Forge Economy Hardening 2 — Eval Integrity

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EVAL_INTEGRITY |
| **Date** | 2026-09-28 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_EVAL_INTEGRITY.md](./DEFINE_API_FORGE_ECONOMY_EVAL_INTEGRITY.md) |
| **DESIGN** | [DESIGN_API_FORGE_ECONOMY_EVAL_INTEGRITY.md](./DESIGN_API_FORGE_ECONOMY_EVAL_INTEGRITY.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Waves** | 2/2 (E1 `8a43c91`, E2 this commit) |
| **Tests** | 1227 passed, 1 skipped (full suite) |
| **Evals** | 10/10 economy evals pass |

---

## Task Execution

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | agentic-quality floor + baseline gates, CLI/MCP | ✅ | all-wrong corpus now fails |
| 2 | `rules/token_eligibility.yaml` + `is_token_eligible` | ✅ | deterministic rows leave the denominator |
| 3 | Run-scoped persist failures | ✅ | `persist_failures_for_run` / `_global` |
| 4 | Hardening oracle on `plan_roles` / `build_delta` + contract invariant case | ✅ | mutated `plan_roles` fails the eval |
| 5 | `confine_dir` + confined `--changed` | ✅ | delta, capsule, evidence |
| 6 | Docs (catalog, threat model EN/PT-BR, economy guide EN/PT-BR, README) + SDD chain | ✅ | critical profile + benchmark |

---

## Issues Encountered

| # | Issue | Resolution |
|---|-------|------------|
| 1 | `subprocess` on Windows did not resolve a relative exe path | Absolute path |
| 2 | ruff PLR0402 on module aliases in tests | Autofix |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| A refused `--changed` item makes the delta `unresolved` (not `degraded`) | Impact of an unreadable file is unknown | stricter status |

---

## Final Status

### Overall: ✅ COMPLETE
