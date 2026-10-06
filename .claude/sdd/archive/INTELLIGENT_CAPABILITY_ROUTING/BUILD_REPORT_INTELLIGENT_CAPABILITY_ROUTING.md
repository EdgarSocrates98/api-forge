# BUILD REPORT: Intelligent Capability Routing

> Implementation report for Intelligent Capability Routing

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | INTELLIGENT_CAPABILITY_ROUTING |
| **Date** | 2026-09-24 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_INTELLIGENT_CAPABILITY_ROUTING.md](../features/DEFINE_INTELLIGENT_CAPABILITY_ROUTING.md) |
| **DESIGN** | [DESIGN_INTELLIGENT_CAPABILITY_ROUTING.md](../features/DESIGN_INTELLIGENT_CAPABILITY_ROUTING.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 18/18 manifest tasks |
| **Files Created** | 13 implementation/test/contract files, plus SDD report |
| **Lines of Code** | 523 production lines in new routing/feedback modules |
| **Build Time** | Not measured as a single wall-clock interval |
| **Tests Passing** | 880/880 repository tests excluding the nested-repository worktree test; that test passed 7/7 from an external clean temp root |
| **Agents Used** | 0 delegated; direct execution because no Task delegation tool was available |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1 | Create versioned routing contracts and registry entries | (direct) | ✅ Complete | - | Applied Pydantic contracts and catalog documentation |
| 2 | Implement eligibility, ranking and deterministic replay trace | (direct) | ✅ Complete | - | Security gate precedes efficiency/quality ranking |
| 3 | Integrate routing into supervisor and RunStore | (direct) | ✅ Complete | - | Routing JSON and trajectory event are persisted |
| 4 | Implement evidence-gated scorecard feedback | (direct) | ✅ Complete | - | Non-PASS gates do not persist quality promotion |
| 5 | Add fixtures, unit tests and integration tests | (direct) | ✅ Complete | - | Acceptance scenarios cover unknowns, safety and replay |
| 6 | Run lint, typing, tests and release gates | (direct) | ✅ Complete | - | Ruff, mypy, pytest, release and SDD checks executed |

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | All implementation and test files | DESIGN patterns plus previously loaded `genai`, `python`, `pydantic`, `testing` and `data-quality` KB patterns |

---

## Files Created

| File | Agent | Verified | Notes |
|------|-------|----------|-------|
| `src/apiforge/contracts/routing.py` | (direct) | ✅ | RoutingRequest, policy, signal, assessment, decision and feedback contracts |
| `src/apiforge/runtime/routing.py` | (direct) | ✅ | Eligibility, explainable lexicographic ranking and stable decision IDs |
| `src/apiforge/runtime/feedback.py` | (direct) | ✅ | Eval-gated scorecard update boundary |
| `docs/contracts/*Routing*-v1.md` | (direct) | ✅ | Contract release-gate documentation |
| `tests/fixtures/agentic_runtime/routing_cases.yaml` | (direct) | ✅ | Efficiency, unknown and safety cases |
| `tests/contracts/test_routing.py` | (direct) | ✅ | Contract validation and registration |
| `tests/runtime/test_routing.py` | (direct) | ✅ | Eligibility, ranking, unknowns and replay |
| `tests/runtime/test_feedback.py` | (direct) | ✅ | PASS/BLOCKED gate behavior and evidence refusal |

---

## Verification Results

### Lint Check

```text
ruff check src tests
All checks passed
```

**Status:** ✅ Pass

### Type Check

```text
mypy src/apiforge
Success: no issues found in 331 source files
```

**Status:** ✅ Pass

### Tests

```text
Targeted routing/supervisor/eval tests: 24 passed
Repository suite with worktree test isolated: 880 passed, 1 skipped
Sandbox worktree test from an external clean temp root: 7 passed
```

**Status:** ✅ Pass

### Release and SDD Gates

```text
scripts.check_release.check_repository: []
apiforge sdd check --root docs/sdd: ok=true, unresolved=[]
DESIGN spec-linter: VERDICT: PASS
```

**Status:** ✅ Pass

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | Pytest default Windows temp root was not accessible | Used a repository-local basetemp for normal tests and an external clean temp root for worktree isolation | Test-environment only |
| 2 | New test basename collided with an existing `tests/rules/test_routing.py` module | Added the contract test package namespace with `tests/contracts/__init__.py` | Resolved |
| 3 | Release gate required catalog and contract docs for new public codes/contracts | Added `AF-RUNTIME-ROUTING` and six contract documents | Resolved |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|-------------------|-------|-----------|
| 1 | How to rank without a validated efficiency baseline | Numeric weights vs stable lexicographic order | Lexicographic efficiency then quality | Matches DESIGN, avoids false precision and preserves deterministic replay |
| 2 | How to treat missing cost/duration/quality | Impute zero vs persist unknown | Explicit `unknown`/`unresolved` signals | Prevents absent evidence from becoming a favorable score |
| 3 | How to preserve existing scorecards | Replace schema vs additive fields | Additive optional fields | Keeps legacy scorecards loadable while adding observations and promotion state |
| 4 | How to handle feedback without a passing eval gate | Persist reputation update vs retain non-pass result only | Do not persist blocked/review promotion | Enforces the existing golden/holdout/mutation quality boundary |
| 5 | Whether to add public contract documentation | Leave registry-only vs document every registered contract | Document all new contracts | Required by the repository release gate and contract registry convention |
| 6 | How to execute specialist assignments | Delegate vs direct implementation | Direct implementation | The current tool surface exposed no Task delegation tool; attribution is explicit in this report |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| Added `docs/contracts/*Routing*-v1.md` and `tests/contracts/__init__.py` | Required by release validation and Python test collection | Documentation and namespace only; no runtime scope expansion |
| Kept the legacy `select_eligible_capabilities` wrapper | Existing callers require compatibility | New supervisor path uses the separated routing service; legacy callers remain stable |
| Did not auto-update scorecards from ordinary supervisor adapter responses | No persisted eval result or passing quality gate exists in a normal run | Prevents unverified runtime output from becoming quality evidence |

---

## Unresolved Gaps (non-blocking)

| Gap | Required Action | Owner |
|---------|-----------------|-------|
| Efficiency baseline and numeric target remain unresolved | Define benchmark corpus and target during `/ship`/benchmark follow-up | Maintainer |
| Exact weighted ranking policy remains intentionally deferred | Add benchmark-backed weights only after observed evidence exists | Maintainer |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Happy path de routing | ✅ | Supervisor persists `routing.json` with selected and fallback order |
| AT-002 | Capability inelegível | ✅ | Eligibility tests preserve refusal code, field and unlock |
| AT-003 | Scorecard não autoriza | ✅ | Risk gate excludes candidates before ranking |
| AT-004 | Dados de eficiência ausentes | ✅ | Unknown signals remain unresolved and non-numeric |
| AT-005 | Scorecard inválido | ✅ | Existing loader preserves `AF-SCORECARD-INVALID` behavior |
| AT-006 | Scorecard ausente | ✅ | Deterministic capability tie-break and unresolved trace tested |
| AT-007 | Avaliação aprovada | ✅ | PASS gate persists promoted scorecard with eval refs |
| AT-008 | Avaliação não aprovada | ✅ | BLOCKED gate returns feedback without persisting promotion |
| AT-009 | Replay determinístico | ✅ | Repeated routing returns equal order and decision ID |
| AT-010 | Falha e fallback | ✅ | Existing bounded scheduler tests plus persisted routing order |
| AT-011 | Ausência de capability elegível | ✅ | Routing decision remains unresolved with `AF-CAPABILITY-ELIGIBILITY` |
| AT-012 | Gate de qualidade incompleto | ✅ | Feedback test preserves blocked gate and no scorecard write |
| AT-013 | Compatibilidade de artefatos | ✅ | Existing scorecard persistence and reload tests pass |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Efficiency improvement | Baseline required before a numeric target | Not measured; signals are recorded when observed | ⏳ Unresolved |
| Ranking determinism | Same inputs produce same ordering | Same order and decision ID in replay test | ✅ |

---

## Data Quality Results

Not an ETL or analytics pipeline. Data-quality validation is covered by the eval gate, explicit signal provenance and scorecard feedback tests.

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] Lint, type and focused verification checks pass
- [x] Repository test suite passes with the nested-repository test executed from a clean external root
- [x] No blocking implementation issues
- [x] Acceptance tests mapped and verified
- [x] Ready for `/ship`

---

## Next Step

```text
/ship .claude/sdd/features/DEFINE_INTELLIGENT_CAPABILITY_ROUTING.md
```
