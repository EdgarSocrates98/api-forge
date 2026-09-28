# DESIGN: API Forge Economy — Selective Agentics (Onda 4)

> Deterministic planners that give each role only its evidence, load expertise on trigger, compress debates into deltas, bound shadow challengers and audit agent uniqueness.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_SELECTIVE_AGENTICS |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md](./DEFINE_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
runtime run
  │ routing plan + economy plan (unchanged)
  ▼
role_context.plan(spec, roles, envelope.context_bytes)
  ├─ target = inputs target= | graph_target=operation:…   case = inputs case= | .apiforge/case
  ├─ ONE capsule (build_capsule, L3, budget = context_bytes)  ── none → unresolved capsule-unavailable
  ├─ class per role kind (rules/role_context.yaml):
  │     specialist → focused            {contract, schema, code, test}      share 0.50
  │     reviewer   → evidence_plus_delta {contract, schema, policy}+artifacts share 0.20
  │     critic     → decision_plus_evidence {policy, contract}+artifacts    share 0.15
  │     referee    → disagreements_only  deltas only                        share 0.15
  ├─ expertise per role: knowledge.selector(intent=outcome, capability, frameworks)
  └─ RoleContextPlan/v1 → role-context.json + ledger rows per role
  ▼
AgentRequest(context_class, context_refs, expertise)   (optional fields; adapters may ignore)
  ▼
L2 … L3 escalation (reviewer gets artifact refs) … L4 flag
  ▼
shadow.decide(run_id, envelope.shadow_share, challenger_order, calls left after reserve)
  └─ sampled → challenger invoked once, artifact → shadow/<cap>.json, agreement vs primary; never in result

debate submit --disagree/--risk/--confidence → PositionDelta/v1 stored per submission
debate packet → RefereePacket/v1 {capsule_id, deltas deduped, disagreement set, evidence union, bytes vs naive}
agents audit → AgentUniqueness/v1 per agent (agents/*.md + runtime catalog + profiles)
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `contracts/selective.py` | ExpertisePick, ExpertiseSelection, RoleContext, RoleContextPlan, PositionDelta, Disagreement, RefereePacket, ShadowDecision, AgentUniqueness | pydantic |
| `contracts/economy.py` | `BudgetEnvelope.context_bytes` (default 32000), `shadow_share` (default 0.0) | optional fields |
| `rules/expertise_triggers.yaml` + `knowledge/selector.py` | Trigger table → packs; bytes loaded vs catalog | YAML |
| `rules/role_context.yaml` + `runtime/role_context.py` | Role classes, shares, planner | YAML |
| `runtime/shadow.py` | Deterministic sampler + decision | hashlib |
| `runtime/supervisor.py` | Wire planner, request fields, shadow | existing |
| `debate/packet.py` + `debate/service.py` | Delta submissions and referee packet | existing store |
| `agentops/agent_audit.py` | Uniqueness gate | frontmatter parse |
| CLI/MCP | `knowledge select`, `debate submit` flags, `debate packet`, `agents audit`, `evals selective-agentics` | typer |
| `evals/selective.py` + corpus | Gates | fixtures |

---

## Key Decisions

### Decision 1: One capsule per run, roles take subsets

**Choice:** Build the capsule once with budget `envelope.context_bytes`; each role filters refs by kind and caps them at `share × context_bytes`.
**Rationale:** §31 shared capsule; one selection cost, per-role transport.
**Consequences:** Roles never see refs outside the capsule; overflow is `AF-ROLE-CONTEXT-BUDGET`, never silent.

### Decision 2: New request fields instead of rewriting `input_refs`

`AgentRequest` gains `context_class`, `context_refs`, `expertise` (defaults empty). `AgentInvocation` and replay digests unchanged, so existing replay tests stay valid.

### Decision 3: No trigger → zero packs

Selector never falls back to "all packs". The capability map adds at most the capability's own packs.

### Decision 4: Shadow is observational

Sampled with `int(sha256(run_id)[:8], 16) % 10000 < round(share × 10000)`; executes only if a challenger exists and calls remain after the verification reserve; recorded in `summary.json` and the result `shadow` block; never alters artifacts, gaps or status.

### Decision 5: Agent audit is report-only

Verdict `keep` when any uniqueness flag is true; `merge-candidate` otherwise, naming agents whose rule areas cover it.

### Decision 6: Profile values

| Profile | context_bytes | shadow_share |
|---------|---------------|--------------|
| economy | 16000 | 0.05 |
| balanced | 32000 | 0.10 |
| deep | 64000 | 0.20 |

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/selective.py`, `economy.py`, registry | Create/Modify | Contracts | @python-developer | — |
| 2 | `src/apiforge/rules/{expertise_triggers,role_context}.yaml`, `economy_profiles.yaml` | Create/Modify | Policy | @python-developer | — |
| 3 | `src/apiforge/knowledge/selector.py` | Create | Lazy expertise | @python-developer | 1,2 |
| 4 | `src/apiforge/runtime/role_context.py` | Create | Planner | @python-developer | 1,2,3 |
| 5 | `src/apiforge/runtime/shadow.py` | Create | Sampler | @python-developer | 1 |
| 6 | `src/apiforge/runtime/{adapters,supervisor}.py` | Modify | Wiring | @python-developer | 4,5 |
| 7 | `src/apiforge/debate/{service,packet}.py` | Modify/Create | Deltas + packet | @python-developer | 1 |
| 8 | `src/apiforge/agentops/agent_audit.py` | Create | Audit | @python-developer | 1 |
| 9 | CLI + MCP | Modify | Surfaces | @python-developer | 3–8 |
| 10 | `src/apiforge/evals/selective.py`, `evals/corpus/selective-agentics/*` | Create | Eval | @test-generator | 3–8 |
| 11 | tests | Create | Unit/integration | @test-generator | all |
| 12 | docs/contracts, catalog, README, skills, SDD chain | Create/Modify | Docs | @code-documenter | all |

---

## Agent Assignment Rationale

Executed inline (coupled, deterministic modules).

---

## Code Patterns

```python
row = RoleContext(role=kind, capability=name, context_class=cls,
                  refs=tuple(r.uri for r in kept), bytes=sum(r.size_bytes for r in kept),
                  budget_bytes=int(share * context_bytes), trimmed=tuple(r.uri for r in dropped))
```

```python
def sampled(run_id: str, share: float) -> bool:
    return int(hashlib.sha256(run_id.encode()).hexdigest()[:8], 16) % 10000 < round(share * 10000)
```

---

## Data Flow

1. Supervisor resolves economy plan → envelope (context_bytes, shadow_share).
2. `role_context.plan` builds capsule and rows for initial + escalation roles; persists.
3. Worker passes row fields in `AgentRequest`.
4. After escalation, `shadow.decide` → optional one challenger call → `shadow/` artifact.
5. Result: `role_context` summary (bytes by role, naive bytes, unresolved) and `shadow` block.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Context Gateway | `build_capsule` in-process | none |
| Knowledge packs | local files | none |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | selector, sampler, packet, audit | `tests/economy/test_selective_*.py` | pytest | AT-001/002/006–010 |
| Integration | supervisor with target + fake adapter | `tests/runtime/test_role_context_supervisor.py` | pytest | AT-003–005, AT-008/009 |
| Parity | CLI == MCP | `tests/mcp/test_selective_tools.py` | CliRunner | 3 tools |
| Eval | corpus gates | `evals selective-agentics` | CLI | DEFINE success criteria |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Trigger file invalid / unknown pack | `AF-EXPERTISE-TRIGGERS-INVALID` | No |
| Role budget overflow | trimmed refs + `AF-ROLE-CONTEXT-BUDGET` unresolved | No |
| Capsule unavailable | `capsule-unavailable:<code>` unresolved, task inputs only | No |
| Bad `--disagree` value | `AF-DEBATE-DELTA-INVALID` | No |
| Shadow without calls | `AF-ECONOMY-SHADOW-BUDGET` reason | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `economy_profiles.yaml` `context_bytes`, `shadow_share` | profile | table above | Envelope |
| `role_context.yaml` | YAML | shipped | Classes, kinds, shares |
| `expertise_triggers.yaml` | YAML | shipped | Triggers |

---

## Security Considerations

- No new I/O beyond local files; shadow never mutates and never gates.
- Role refs are ctx hashes; expansion still re-verifies content.

---

## Observability

- `role-context.json`, ledger rows `runtime role:<kind>`, `summary.json.shadow`.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md`
