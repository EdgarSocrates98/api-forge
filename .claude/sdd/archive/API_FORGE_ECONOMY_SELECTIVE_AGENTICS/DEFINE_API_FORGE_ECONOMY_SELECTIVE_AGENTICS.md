# DEFINE: API Forge Economy — Selective Agentics (Onda 4)

> Each role gets the minimum evidence it needs, packs load only on trigger, debates exchange deltas over one capsule, challengers run in a bounded shadow, and redundant agents are flagged.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_SELECTIVE_AGENTICS |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md` |

---

## Problem Statement

Every runtime invocation receives the same full task inputs regardless of role, expertise packs are never selected from the intent, debate positions are free text replicated to the referee, planned challengers are never measured, and no gate flags agents that own no unique capability. Multi-agent runs therefore pay parent-sized context per subagent and cannot learn whether extra agents are worth their cost.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Agent host | Executes runtime invocations | Subagents inherit the whole context |
| Operator / CI | Runs `runtime run|debate` | Cannot bound or see per-role context and shadow cost |
| Maintainer | Owns the agent catalog | No evidence of which agents are redundant |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | G1: `ExpertiseSelection/v1` from declarative triggers (intent keywords, frameworks, capabilities); no trigger → 0 packs + `unresolved` (§26–27) |
| **MUST** | G2: `RoleContextPlan/v1` with context classes `focused`, `evidence_plus_delta`, `decision_plus_evidence`, `disagreements_only` and per-role byte budgets from the envelope `context_bytes` (§86–87) |
| **MUST** | G3: Supervisor builds one capsule per run when the TaskSpec names a target, passes each invocation its role refs (`AgentRequest.context_class/context_refs`), persists `role-context.json` and attributes bytes per role in the ledger |
| **MUST** | G4: `PositionDelta/v1` on `debate submit` (disagreements, risks, confidence) and `debate packet` = capsule id + deduped deltas + disagreement set (§30–32, §84–85) |
| **MUST** | G5: Shadow budget: `BudgetEnvelope.shadow_share` per profile, deterministic sampling, sampled challenger executed only from calls left after the verification reserve, artifact stored under `shadow/` and never counted in the result (§36–38) |
| **SHOULD** | G6: `agents audit` → `AgentUniqueness/v1` rows with unique capability/expertise/validator/decision-role flags and `keep|merge-candidate` verdict (§29) |
| **SHOULD** | G7: CLI + MCP parity (`knowledge select`, `debate packet`, `agents audit`, `runtime run` output `role_context` and `shadow`) |
| **SHOULD** | G8: `evals selective-agentics` corpus with gates |

---

## Success Criteria

- [ ] Expertise selection precision = recall = 1.0 on the corpus; ≥ 1 no-trigger case selects 0 packs.
- [ ] Role context: reviewer, critic and referee bytes each ≤ primary bytes; total role bytes ≤ 60% of naive replication (full capsule to every role).
- [ ] Referee packet ≤ 50% of naive (all submissions + capsule per side) with 100% of evidence ids preserved.
- [ ] Shadow sampled rate within ±2 percentage points of `shadow_share` over 10000 synthetic run ids; final status identical with shadow on/off.
- [ ] `agents audit` byte-identical across two runs; every catalog agent receives a verdict.
- [ ] Existing runtime/economy tests green (routing decisions unchanged).

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Pack selection | intent "make PaymentRequest.description nullable in OpenAPI" | `knowledge select` | `openapi-31`, `json-schema`, `api-lifecycle` only |
| AT-002 | No trigger | intent "hello" | select | 0 packs, `unresolved: no-expertise-trigger` |
| AT-003 | Role refs | TaskSpec with `target=POST /payments` + analyzed case | `runtime run` | primary refs ⊇ code/schema; referee refs = none until deltas; `role-context.json` persisted |
| AT-004 | No target | TaskSpec without target | run | roles get task inputs only; `capsule-unavailable` in role context unresolved |
| AT-005 | Byte budget | tiny envelope context budget | run | refs trimmed per role, `AF-ROLE-CONTEXT-BUDGET` recorded, never silent |
| AT-006 | Delta submit | open debate | submit with `--disagree point=reason` | stored with disagreements, risks, confidence |
| AT-007 | Referee packet | 2 sides with deltas | `debate packet` | packet has capsule id, deltas, disagreement set, all evidence ids |
| AT-008 | Shadow sampled | run id hashing under share | run | challenger executed in shadow; result artifacts unchanged |
| AT-009 | Shadow not sampled / no calls | share 0 or no calls left | run | `shadow.executed=false` with reason code |
| AT-010 | Agent audit | catalog | `agents audit` | verdict per agent, overlaps named |

---

## Out of Scope

- Reviewer ROI / information-gain learning (Wave 6).
- Prompt compiler, stable prefixes (extras).
- Automatic agent removal; changing routing decisions.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Offline, no provider SDK, no LLM summarization | Deterministic planners |
| Technical | Optional fields only on existing contracts | Legacy payloads validate |
| Technical | AF codes cataloged with field/unlock | Catalog + release prefixes |
| Process | Targeted tests per wave; full suite at program end | — |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/{knowledge/selector.py,runtime/role_context.py,runtime/shadow.py,debate/packet.py,agentops/agent_audit.py,contracts/selective.py}` + rules | Additive modules |
| **KB Domains** | pydantic, testing, genai | — |
| **IaC Impact** | None | — |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Fake adapter ignores unknown request fields | Replay tests break | [x] `AgentRequest` owned by us; fields optional |
| A-002 | Pack frontmatter carries areas/summary | Triggers need own mapping | [x] `pack.yaml` |
| A-003 | Agent docs carry `rule_areas`/`executors` | Audit incomplete | [x] frontmatter sample |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Concrete code evidence |
| Users | 3 | Host, operator, maintainer |
| Goals | 3 | MoSCoW, section-mapped |
| Success | 3 | Numeric gates |
| Scope | 2 | Host honoring refs is outside core |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial version |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md`
