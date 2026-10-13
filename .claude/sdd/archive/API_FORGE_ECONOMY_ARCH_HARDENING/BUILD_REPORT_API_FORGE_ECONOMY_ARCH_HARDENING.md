# BUILD REPORT: API Forge Economy Architecture Hardening

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_ARCH_HARDENING |
| **Date** | 2026-09-28 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_ARCH_HARDENING.md](./DEFINE_API_FORGE_ECONOMY_ARCH_HARDENING.md) |
| **DESIGN** | [DESIGN_API_FORGE_ECONOMY_ARCH_HARDENING.md](./DESIGN_API_FORGE_ECONOMY_ARCH_HARDENING.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Waves** | 4/4 (H1 `a84b650`, H2 `f460b29`, H3 `afefb03`, H4 this commit) |
| **Tests** | 1218 passed, 1 skipped (full suite) |
| **Evals** | 8 existing economy evals pass; `economy-hardening` 15/15; `agentic-quality` 1.0 per profile |

---

## Task Execution

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Source resolver + verified case reader (H1) | ✅ | gateway, evidence, delta, load_graph, receipt emit |
| 2 | Class pools + RoleContext/RoleContextPlan validators (H2) | ✅ | absolute envelope gate in eval |
| 3 | ControlPlane `calls_by_kind` + `record_call`; shadow accounted + mode (H2) | ✅ | checkpoint = real calls |
| 4 | Token coverage + auditable ledger rows (H2) | ✅ | `AF-ECONOMY-LEDGER-PERSIST` |
| 5 | Structured L0 proofs (`ProofReceipt/v1`) (H3) | ✅ | textual mention ⇒ L1 |
| 6 | Cache fall-through + timestamp validation (H3) | ✅ | |
| 7 | Knowledge generation key + Unicode retrieval (H3) | ✅ | |
| 8 | Phase quality/budget status, routing unresolved, delta degraded (H4) | ✅ | |
| 9 | `evals economy-hardening`, `evals agentic-quality`, matrix `claim_scope` (H4) | ✅ | CLI + MCP |
| 10 | CI: PR token for auto-merge + daily schedule (H4) | ✅ | secret must be configured |

---

## Issues Encountered

| # | Issue | Resolution |
|---|-------|------------|
| 1 | Poisoned-fact test selected no fact | Target `code.route` facts |
| 2 | Bash heredoc mangles backslashes | Patch scripts written with Write |
| 3 | Search on a custom knowledge root requires trigger packs | Tests stub the selector |
| 4 | `sdd check`: high risk requires the `critical` profile and a benchmark phase | Profile raised, `benchmark.md` added |
| 5 | A forged ProofReceipt still mentions its kind in the step | Reaches L1 at most (never L0); asserted as such |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| `ControlRun.calls_by_kind` records `step` and `shadow` (not primary/review) | Step kinds are not known to the control plane | total accounting unchanged |
| Contract/project inputs refused → replaced by a never-existing path | Keeps downstream readers unchanged | refused input yields no code refs |
| `evidence emit_receipt` path containment added | Same bug class found while auditing case readers | stricter receipts |

---

## Final Status

### Overall: ✅ COMPLETE
