# DESIGN: API Forge Economy — Freshness Watch, Live Gating, Progressive Verification and Resume Checkpoint (Onda 8)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_FRESHNESS_RESUME |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE](./DEFINE_API_FORGE_ECONOMY_FRESHNESS_RESUME.md) |
| **Status** | ✅ Shipped |

---

## Architecture

```text
knowledge/*/pack.yaml ─┐
upstream manifest.json ┴─> knowledge/watch.py ──> FreshnessWatch/v1
question + rules/live_evidence_triggers.yaml ──> evidence/live_gate.py ──> LiveEvidenceDecision/v1
static verdict + TestSlice/v1 + runtime verdict ──> verification/progressive.py ──> VerificationEscalation/v1
profile envelope + rules/phase_budgets.yaml + usage ──> economy/phase_budget.py ──> PhaseBudgetPlan/v1
execute_run / resume_existing_run ──> runtime/economy_checkpoint.py ──> EconomyCheckpoint/v1 (economy_checkpoint.json)
```

## Decisions (inline ADRs)

| # | Decision | Rationale | Rejected |
|---|---|---|---|
| D1 | Manifest is local JSON, read-only | §95 refresh is a separate workflow | live fetch |
| D2 | Watch measures the window from the pack `verified` date (build deviation: `verify_pack_freshness` measures receipt age, a different question) | the pack's own validation age is what goes stale | receipt age |
| D3 | Gate: runtime terms win only when present; ambiguous → static first with `escalate_if_unanswered` | cheapest first (§97) | default-live |
| D4 | Escalation table is code, not YAML | six fixed transitions; safety-critical | configurable ladder |
| D5 | Resume pins `max(checkpoint.effective, requested)` by profile order | never downgrade mid-run | re-resolve |
| D6 | verify/secure `protected: true` → overrun reported, never `cut` | §100 | uniform cut |

## File Manifest

| # | File | Action | Purpose |
|---|---|---|---|
| 1 | `src/apiforge/contracts/economy_resume.py` | create | 5 contracts + rows |
| 2 | `src/apiforge/contracts/knowledge.py` | modify | `PackFreshness` + `source_version`, `expires_at`, `upstream` |
| 3 | `src/apiforge/knowledge/watch.py` | create | watch |
| 4 | `src/apiforge/rules/live_evidence_triggers.yaml`, `evidence/live_gate.py` | create | gate |
| 5 | `src/apiforge/verification/progressive.py` | create | escalation |
| 6 | `src/apiforge/rules/phase_budgets.yaml`, `economy/phase_budget.py` | create | phase budgets |
| 7 | `src/apiforge/runtime/economy_checkpoint.py`, `runtime/supervisor.py` | create/modify | checkpoint write/load, resume pin |
| 8 | `src/apiforge/cli_resume.py`, `cli.py`, `mcp/tools.py` | create/modify | 5 verbs, 5 tools |
| 9 | `src/apiforge/evals/freshness_resume.py`, corpus, `cli` evals verb | create | eval |
| 10 | tests, contract docs, catalog, README, skill mirrors, SDD chain | create/modify | gates |

## Escalation table (D4)

| static | test | runtime | action | next |
|---|---|---|---|---|
| any | failed | — | stop (confirmed) | — |
| any | passed | — | stop (verified) | — |
| any | missing | — | run_tests | test |
| any | inconclusive | missing | escalate | live_read_only |
| any | inconclusive | confirmed/clear | stop | — |
| any | inconclusive | inconclusive | unresolved | — |

## Testing Strategy

`tests/economy/test_freshness_resume.py`: one test per AT; supervisor resume
test with the fake adapter; eval `evals freshness-resume` with gates.

## Next Step

`/build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_FRESHNESS_RESUME.md`
