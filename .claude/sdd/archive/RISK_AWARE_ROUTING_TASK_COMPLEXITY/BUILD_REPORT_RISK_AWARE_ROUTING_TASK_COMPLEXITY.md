# BUILD REPORT: Risk-Aware Routing and Task Complexity

> Implementation report for the deterministic, offline-first MVP A.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | RISK_AWARE_ROUTING_TASK_COMPLEXITY |
| **Date** | 2026-09-25 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_RISK_AWARE_ROUTING_TASK_COMPLEXITY.md](../features/DEFINE_RISK_AWARE_ROUTING_TASK_COMPLEXITY.md) |
| **DESIGN** | [DESIGN_RISK_AWARE_ROUTING_TASK_COMPLEXITY.md](../features/DESIGN_RISK_AWARE_ROUTING_TASK_COMPLEXITY.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 33/33 manifest files implemented or updated |
| **Files Created** | 6 manifest files |
| **Lines of Code** | 1,317 insertions, 50 deletions across 35 files in `ee9363d` |
| **Build Time** | Final full suite: 50.08s |
| **Tests Passing** | Focused: 46 passed; final full suite: 950 passed, 2 skipped |
| **Agents Used** | 0 delegated; direct build with specialist review lenses |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | Add risk/complexity contracts and registry exports | (direct) | ✅ Complete | Followed @api-agentic-orchestrator and @api-governance-reviewer assignments |
| 2 | Extend routing request, decision and plan compatibly | (direct) | ✅ Complete | Existing v1 fields remain valid; additions are optional or additive |
| 3 | Implement pure policy classifier and local YAML rules | (direct) | ✅ Complete | No provider, network, database or time dependency |
| 4 | Integrate classify-before-rank and role composition | (direct) | ✅ Complete | Unknown signals remain unresolved; assessment blockers gate the plan |
| 5 | Persist routing artifacts and runtime event provenance | (direct) | ✅ Complete | Assessment, evidence and unresolved state are serialized |
| 6 | Project routing artifacts through runtime, CLI, TUI and governance | (direct) | ✅ Complete | Shared read-only payload and typed view fields |
| 7 | Add contracts, runtime, integration, parity and evaluation tests | (direct) | ✅ Complete | Golden/holdout/mutation/adversarial fixture coverage |
| 8 | Add contract documentation and this build report | (direct) | ✅ Complete | Clean full-suite verification completed |

No delegated Task tool was available in the current Codex surface, so all
manifest work was performed directly and checked against the specialist
ownership rationale in the DESIGN.

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | 1–33 | Deterministic contracts, policy compiler, runtime routing, read-only projections and tests using the DESIGN and loaded KB patterns |
| @api-adversarial-critic | Review lens | Checked silent fallback, evidence loss, order dependence, role bypass and unresolved handling; no delegated mutation was performed |

---

## Files Created

| File | Agent | Verified |
| ---- | ----- | -------- |
| `src/apiforge/contracts/risk_complexity.py` | (direct) | ✅ |
| `src/apiforge/runtime/risk_complexity.py` | (direct) | ✅ |
| `docs/contracts/RiskComplexityAssessment-v1.md` | (direct) | ✅ |
| `tests/contracts/test_risk_complexity.py` | (direct) | ✅ |
| `tests/runtime/test_risk_complexity.py` | (direct) | ✅ |
| `tests/fixtures/agentic_runtime/risk_complexity_cases.yaml` | (direct) | ✅ |

All remaining files from the 33-file DESIGN manifest were updated and verified
through the focused suite or static checks.

---

## Verification Results

### Lint Check

```text
ruff check .
All checks passed!
```

**Status:** ✅ Pass

### Type Check

```text
mypy src/apiforge
Success: no issues found in 362 source files
```

**Status:** ✅ Pass

### Tests

```text
Focused routing/projection/evaluation suite: 46 passed, 8 existing warnings.
Final clean-worktree full run: 950 passed, 2 skipped in 50.08s.
```

An earlier full run exposed two environment-sensitive failures: one requires a
clean Git worktree, and the other was caused by placing pytest's basetemp
inside the repository, making generated nested Git fixtures look like
repository state. The final rerun used an external basetemp after the
implementation commit and passed.

| Test Area | Result |
|-----------|--------|
| Risk/complexity contracts | ✅ Pass |
| Pure classifier and routing | ✅ Pass |
| Supervisor persistence and runtime | ✅ Pass |
| Application/CLI/TUI projection parity | ✅ Pass |
| Evaluation gate and fixture matrix | ✅ Pass |
| Full suite clean-worktree rerun | ✅ Pass — 950 passed, 2 skipped |

---

## Issues Encountered

| # | Issue | Resolution |
|---|-------|------------|
| 1 | Existing sensitive routing test would select the newly added critic as primary | Required role candidates are appended after eligible specialists, preserving primary selection semantics |
| 2 | Moderate tasks add the required `task-review` invocation | Updated the runtime experience expectation from five to six reused invocations; the review role is now explicit policy behavior |
| 3 | Unknown routing signals incorrectly made the plan `blocked` | Preserved all signal diagnostics in `unresolved`, but gate state now uses only assessment blockers and missing required roles |
| 4 | pytest default temp root lacked Windows access | Focused tests use an explicit workspace temp root; final full run uses a path outside the repository |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|-------------------|-------|-----------|
| 1 | Specialist delegation surface was unavailable | Delegate through Task tool vs direct execution | Direct execution | The available Codex tool surface has no Task tool; direct work remained within the DESIGN manifest and was checked with specialist review lenses |
| 2 | Backward-compatible field naming for task size | Accept only `task_size` vs accept legacy-style `size` too | `AliasChoices("task_size", "size")` | Preserves old/request-fixture compatibility while serializing one canonical `task_size` field |
| 3 | Meaning of unresolved ranking signals | Treat every unknown signal as a hard block vs preserve it without blocking | Preserve diagnostics; block only assessment gaps | Existing routing intentionally supports unknown signals; evidence must remain visible without inventing a refusal |
| 4 | Runtime composition for moderate tasks | Keep the old specialist-only set vs execute the policy-required reviewer | Execute the reviewer | The MVP acceptance explicitly makes complexity affect review composition; the changed invocation count is recorded and tested |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| `RoutingPlan/v1` includes `gate_state` and concrete assessment effect fields | Required to expose composition and gating without recomputation in projections | Additive fields; role disjointness and fallback limits remain unchanged |
| `ExperienceView` exposes typed `routing` and `routing_plan` fields in addition to payload | Makes projection parity inspectable while retaining the canonical generic payload | Existing callers remain valid because fields default to `None` |
| `src/apiforge/runtime/registry.py` accepts additive role candidates | The router must include policy-required reviewer/critic/referee capabilities without changing legacy requested-capability selection | Small runtime seam extension; existing capability ordering and eligibility remain covered |
| No separate sidecar assessment file was persisted | DESIGN chose `RoutingDecision/v1` as the canonical artifact | Prevents projection drift and keeps replay identity bound to the decision |

---

## Blockers

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| None | No blocking action remains; hand off to `/ship` | build-agent |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Deterministic replay | ✅ Pass | Stable assessment IDs and focused replay tests |
| AT-002 | Risk-sensitive policy | ✅ Pass | Safety-risk policy and routing tests |
| AT-003 | Complexity-sensitive composition | ✅ Pass | Size/proof fixtures and reviewer/critic plan test |
| AT-004 | Unresolved evidence | ✅ Pass | Blocked assessment retains `AF-CAPABILITY-ELIGIBILITY`, field and unlock |
| AT-005 | Canonical projection parity | ✅ Pass | Runtime, application, CLI, fallback and e2e parity tests |
| AT-006 | Existing routing compatibility | ✅ Pass | Existing routing, plan and expertise tests |
| AT-007 | Evaluation coverage | ✅ Pass | Expanded adaptive routing gate with all four mandatory kinds |
| AT-008 | Offline safety boundary | ✅ Pass | Local fake adapter/runtime tests; no provider/network path added |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Replay determinism | Identical local inputs produce identical IDs | Focused deterministic tests pass | ✅ |
| External dependency calls | Zero in MVP classifier/routing path | No provider/network/database integration added | ✅ |

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] Focused verification checks pass
- [x] Full clean-worktree test suite pass recorded
- [x] No feature blocking issues
- [x] Acceptance tests verified by focused coverage
- [x] Ready for `/ship`

---

## Next Step

Archived with the SDD phase artifacts after final verification.
