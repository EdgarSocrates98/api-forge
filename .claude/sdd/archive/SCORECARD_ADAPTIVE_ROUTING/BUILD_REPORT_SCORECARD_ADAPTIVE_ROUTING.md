# BUILD REPORT: Scorecard-Adaptive Routing

> Implementation report for deterministic, evidence-gated scorecard adaptation B.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | SCORECARD_ADAPTIVE_ROUTING |
| **Date** | 2026-09-25 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_SCORECARD_ADAPTIVE_ROUTING.md](../features/DEFINE_SCORECARD_ADAPTIVE_ROUTING.md) |
| **DESIGN** | [DESIGN_SCORECARD_ADAPTIVE_ROUTING.md](../features/DESIGN_SCORECARD_ADAPTIVE_ROUTING.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 19/19 manifest tasks |
| **Files Created** | 10 new contract/runtime/docs/test/fixture files |
| **Files Touched** | 21 files in implementation commit `3dad4f4` |
| **Lines of Code** | 638 insertions, 20 deletions |
| **Build Time** | Final full suite completed in 49.71s |
| **Tests Passing** | 961 passed, 2 skipped, 8 existing warnings |
| **Agents Used** | 0 delegated; direct execution because no Task tool was available |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1 | Add adaptive policy and candidate/assessment contracts | (direct) | ✅ Complete | - | Implemented frozen v1 contracts and validators |
| 2 | Extend RoutingPolicy, RoutingDecision and RoutingPlan additively | (direct) | ✅ Complete | - | Preserved A fields and legacy defaults |
| 3 | Register and export the new contracts | (direct) | ✅ Complete | - | Release documentation gate also verified |
| 4 | Implement pure scorecard lane classifier | (direct) | ✅ Complete | - | Champion, challenger and unresolved paths are explicit |
| 5 | Integrate scorecard policy loading | (direct) | ✅ Complete | - | Local YAML policy is versioned and bounded |
| 6 | Integrate adaptive ordering after risk/complexity ranking | (direct) | ✅ Complete | - | A remains authoritative for objective order and roles |
| 7 | Preserve scorecard evidence and unresolved state | (direct) | ✅ Complete | - | Evidence contributes to decision identity and output |
| 8 | Add challenger metadata to plan construction | (direct) | ✅ Complete | - | Metadata is read-only and not an implicit execution role |
| 9 | Document adaptive contracts and policy | (direct) | ✅ Complete | - | Candidate, policy and assessment docs added |
| 10 | Add contract registration and validator tests | (direct) | ✅ Complete | - | Bounds and champion invariants covered |
| 11 | Add lane classifier tests | (direct) | ✅ Complete | - | Fresh, missing, unpromoted and stale paths covered |
| 12 | Add routing integration tests | (direct) | ✅ Complete | - | Existing routing and replay behavior remain covered |
| 13 | Add plan compatibility tests | (direct) | ✅ Complete | - | Existing plans default to no challenger metadata |
| 14 | Add scorecard fixture matrix | (direct) | ✅ Complete | - | Golden, holdout, mutation and adversarial cases |
| 15 | Add adaptive evaluation gate | (direct) | ✅ Complete | - | Missing adversarial evidence blocks the gate |
| 16 | Verify release contract documentation | (direct) | ✅ Complete | - | Added both registered contract docs required by release gate |
| 17 | Run focused tests and static checks | (direct) | ✅ Complete | - | Focused suite passed before full run |
| 18 | Run clean external-basetemp full suite | (direct) | ✅ Complete | - | Avoided repository Git-fixture contamination on Windows |
| 19 | Update SDD statuses and produce this report | (direct) | ✅ Complete | - | DEFINE/DESIGN are ready for `/ship` |

**Legend:** ✅ Complete | 🔄 In Progress | ⏳ Pending | ❌ Blocked

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | All 21 implementation files | Typed contracts, pure policy transformation, routing integration, local YAML and fixture-driven verification |
| @python-developer | Design assignment only | Python contracts/runtime pattern match; no delegated Task execution was available |
| @test-generator | Design assignment only | Contract/evaluation test pattern match; no delegated Task execution was available |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
|------|-------|-------|----------|-------|
| `src/apiforge/contracts/scorecard_routing.py` | 80 | (direct) | ✅ | Policy, candidate and assessment v1 contracts |
| `src/apiforge/runtime/scorecard_routing.py` | 124 | (direct) | ✅ | Pure lane classification and deterministic ordering |
| `docs/contracts/ScorecardCandidateAssessment-v1.md` | 25 | (direct) | ✅ | Release-gate contract documentation |
| `docs/contracts/ScorecardRoutingAssessment-v1.md` | 26 | (direct) | ✅ | Canonical assessment documentation |
| `docs/contracts/ScorecardRoutingPolicy-v1.md` | 18 | (direct) | ✅ | Policy documentation |
| `tests/contracts/test_scorecard_routing.py` | 46 | (direct) | ✅ | Contract validators and registry |
| `tests/runtime/test_scorecard_routing.py` | 87 | (direct) | ✅ | Lane, freshness, bound and replay behavior |
| `tests/fixtures/agentic_runtime/scorecard_adaptive_cases.yaml` | 22 | (direct) | ✅ | Local lane fixture matrix |
| `tests/evals/cases/scorecard_adaptive_routing.yaml` | 38 | (direct) | ✅ | Mandatory eval categories |
| `tests/evals/test_scorecard_adaptive_routing_gate.py` | 53 | (direct) | ✅ | Eval gate and adversarial requirement |

---

## Verification Results

### Lint Check

```text
ruff check .
All checks passed!
```

**Status:** ✅ Pass

Changed new files also pass `ruff format --check`. A repository-wide format check still reports pre-existing unformatted archive/vendor/baseline files; those files were not reformatted because they are outside this feature's scope.

### Type Check

```text
mypy src/apiforge
Success: no issues found in 364 source files
```

**Status:** ✅ Pass

### Release and SDD Checks

```text
python scripts/check_release.py
API Forge release gate: PASS

DEFINE spec-lint: PASS
DESIGN spec-lint: PASS
apiforge sdd check --root docs/sdd
EXIT_CODE=0
```

**Status:** ✅ Pass

### Tests

```text
Focused adaptive/routing suite: 23 passed
Final clean external-basetemp full suite: 961 passed, 2 skipped in 49.71s
```

| Test Area | Result |
|-----------|--------|
| Adaptive contracts and registry | ✅ Pass |
| Champion/challenger/unresolved classifier | ✅ Pass |
| Freshness and evidence preservation | ✅ Pass |
| Routing and plan compatibility | ✅ Pass |
| Golden/holdout/mutation/adversarial adaptive gate | ✅ Pass |
| Existing feedback and promotion gates | ✅ Pass |
| Full repository suite | ✅ Pass — 961 passed, 2 skipped |

**Status:** ✅ 961 passed, 2 skipped; 8 existing Pydantic/cache warnings

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | First full run found the registered `ScorecardCandidateAssessment/v1` without its release-gate documentation | Added `docs/contracts/ScorecardCandidateAssessment-v1.md` and reran the release gate | One correction cycle |
| 2 | Release gate then found the registered `ScorecardRoutingPolicy/v1` without its documentation | Added `docs/contracts/ScorecardRoutingPolicy-v1.md` and reran the release gate | One correction cycle |
| 3 | Repository-wide Ruff format check reports pre-existing unformatted archive/vendor/baseline files | Verified all new files are formatted; kept unrelated historical files unchanged | No implementation impact |
| 4 | Pytest cache emits existing Windows directory warnings in the repository | Ran the final suite with an external basetemp and preserved the warning as non-blocking evidence | No test impact |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|-------------------|-------|-----------|
| 1 | Delegation surface unavailable | Delegate to specialist Task agents vs direct execution | Direct execution | No Task tool was available; the manifest and specialist ownership rationale were still followed and recorded |
| 2 | Adaptive ranking shape | Weighted scalar vs explicit lanes | Champion/challenger/unresolved lanes | Preserves freshness and evidence semantics and prevents silent starvation |
| 3 | Stale scorecard behavior | Drop candidate, trust history, or retain unresolved | Retain unresolved | Eligibility and evidence freshness are separate; diagnostics must remain visible |
| 4 | Challenger execution semantics | Execute shadow work automatically vs record bounded metadata | Record bounded metadata only | Avoids hidden runtime cost and keeps live shadow promotion outside B MVP |
| 5 | Scorecard input ordering | Trust caller order vs canonicalize snapshots | Sort scorecards by canonical serialized content | Identical scorecard sets must produce identical replay identity |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| No new CLI/TUI surface was added | DEFINE explicitly marked a dedicated explainability surface as COULD and existing projections serialize the canonical decision | No behavior loss; future UI can consume the persisted assessment |
| `challenger_order` is plan metadata rather than an execution role | Live shadow execution is out of scope and adding it would change runtime budgets | The challenge opportunity is auditable without implicit side effects |
| Release-gate contract docs were added after the first full run | The registry-to-doc convention exposed both new registered contract names | Documentation is now complete and the release gate passes |

---

## Blockers (if any)

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| None | No blocking action remains; hand off to `/ship` | build-agent |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Deterministic adaptive replay | ✅ Pass | Stable assessment/decision/plan tests and permutation-safe scorecard mapping |
| AT-002 | Fresh champion preference | ✅ Pass | Fresh promoted lane and routing integration tests |
| AT-003 | Bounded challenger opportunity | ✅ Pass | Challenger slot contract and classifier tests |
| AT-004 | Freshness safety | ✅ Pass | Stale/unresolved lane and gap-preservation tests |
| AT-005 | Evidence preservation | ✅ Pass | Assessment refs flow into `RoutingDecision/v1` and plan evidence |
| AT-006 | Legacy compatibility | ✅ Pass | Existing routing, plan, feedback and full-suite tests |
| AT-007 | Feedback gate integrity | ✅ Pass | Existing scorecard feedback gate tests remain green |
| AT-008 | Policy mutation replay | ✅ Pass | Adaptive mutation/adversarial evaluation gate |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| External calls in adaptive routing | Zero | No provider/network/database integration added | ✅ |
| Replay identity | Stable for identical local inputs | Assessment and decision replay tests pass | ✅ |
| Full suite duration | Local verification only; no production SLO claim | 49.71s measured on final run | ✅ |

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] All verification checks pass
- [x] All tests pass
- [x] No blocking issues
- [x] Acceptance tests verified
- [x] Ready for `/ship`

---

## Next Step

Archived with all SDD phase artifacts after final verification.
