# BUILD REPORT: API Forge Economy — Selective Agentics (Onda 4)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_SELECTIVE_AGENTICS |
| **Date** | 2026-09-28 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md](./DEFINE_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md) |
| **DESIGN** | [DESIGN_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md](./DESIGN_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 12/12 |
| **Files Created** | 30 |
| **Files Modified** | 14 |
| **Tests** | 209 passed, 1 skipped (targeted) |
| **Eval** | `evals selective-agentics` 13 cases, 6/6 gates |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | Contracts + envelope fields | (direct) | ✅ | 6 contracts; `context_bytes`, `shadow_share` |
| 2 | Trigger + role policy YAML | (direct) | ✅ | 34 keyword triggers over 38 packs |
| 3 | `knowledge/selector.py` | (direct) | ✅ | |
| 4 | `runtime/role_context.py` | (direct) | ✅ | one capsule per run |
| 5 | `runtime/shadow.py` | (direct) | ✅ | |
| 6 | Supervisor + `AgentRequest` wiring | (direct) | ✅ | role fields, escalation artifact refs, shadow |
| 7 | Debate deltas + packet | (direct) | ✅ | |
| 8 | Agent audit | (direct) | ✅ | |
| 9 | CLI + MCP | (direct) | ✅ | 3 tools, submit flags |
| 10 | Eval + corpus | (direct) | ✅ | |
| 11 | Tests | (direct) | ✅ | 3 modules |
| 12 | Docs, catalog, README, skills, SDD chain | (direct) | ✅ | `sdd check` ok |

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | 44 | Coupled deterministic modules |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
|------|-------|-------|----------|-------|
| `src/apiforge/contracts/selective.py` | ~140 | (direct) | ✅ | |
| `src/apiforge/knowledge/selector.py` | ~170 | (direct) | ✅ | |
| `src/apiforge/runtime/{role_context,shadow}.py` | ~260 | (direct) | ✅ | |
| `src/apiforge/debate/packet.py`, `src/apiforge/agentops/agent_audit.py` | ~200 | (direct) | ✅ | |
| `src/apiforge/{application/selective,cli_selective}.py`, `src/apiforge/evals/selective.py` | ~330 | (direct) | ✅ | |
| `src/apiforge/rules/{expertise_triggers,role_context}.yaml` | ~150 | (direct) | ✅ | |
| `evals/corpus/selective-agentics/*` (13) + 3 test modules + 6 contract docs | — | (direct) | ✅ | |

---

## Verification Results

### Lint Check

```text
ruff check + ruff format on touched files: clean
```

### Type Check

```text
mypy src/apiforge: Success: no issues found in 402 source files
```

### Tests

| Test | Result |
|------|--------|
| `tests/economy/test_selective_agentics.py` | ✅ 11 |
| `tests/runtime/test_role_context_supervisor.py` | ✅ 3 |
| `tests/mcp/test_selective_tools.py` | ✅ 4 |
| `tests/economy tests/runtime tests/contracts tests/mcp/test_tools.py` | ✅ |
| **Total targeted** | **209 passed, 1 skipped** |

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | 1000 synthetic ids gave 11.1%/22.2% for 10%/20% shares (sampling variance) | 10000 ids; hash sampling is uniform (4.9/10.1/20.5%) | small |
| 2 | Economy profile trims all challengers, so shadow never had candidates | Shadow draws from the routing plan before economy trims | none |
| 3 | Shadow reason code inside an f-string escaped the release AF parity scan | Module constant `SHADOW_BUDGET` | none |

---

## Autonomous Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Keep `input_refs` unchanged, add request fields | Replay digests and golden runs stay valid |
| 2 | Referee packet counts capsule content once, naive counts it per participant + referee | Matches §31 transport model |
| 3 | Audit criteria use declared data only | Deterministic; a merge candidate is an evidence gap, not a verdict to delete |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| Shadow sample-size gate uses 10000 ids | Statistical tolerance of ±2 pp needs it | DEFINE updated |
| Shadow candidates taken pre-trim | Economy has 0 challenger slots | Documented in ship |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Pack selection | ✅ | `test_selector_loads_only_triggered_packs` |
| AT-002 | No trigger | ✅ | same |
| AT-003 | Role refs | ✅ | `test_each_invocation_gets_its_role_context` |
| AT-004 | No target | ✅ | `test_without_target_roles_get_no_capsule`, `test_no_target_means_no_capsule_refs` |
| AT-005 | Byte budget | ✅ | `test_tight_budget_trims_and_says_so` |
| AT-006 | Delta submit | ✅ | `test_debate_submit_deltas_and_packet_parity` |
| AT-007 | Referee packet | ✅ | `test_position_deltas_and_referee_packet` |
| AT-008 | Shadow sampled | ✅ | `test_shadow_runs_outside_the_result` |
| AT-009 | Shadow not sampled / no calls | ✅ | `test_shadow_sampling_is_deterministic_and_bounded` |
| AT-010 | Agent audit | ✅ | `test_agent_audit_is_deterministic_and_complete`, `test_agents_audit_parity` |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Expertise loaded vs catalog | ≪ catalog | 6–15 KB of 218 KB | ✅ |
| Role bytes vs naive | ≤ 60% | 40–44% | ✅ |
| Referee packet vs naive | ≤ 50% | 34–35% | ✅ |
| Shadow rate error | ≤ 2 pp | ≤ 0.6 pp | ✅ |

---

## Final Status

### Overall: ✅ COMPLETE

- [x] All tasks from manifest completed
- [x] Targeted verification passes
- [x] Acceptance tests verified
- [ ] Full suite — deferred to program end

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md`
