# BUILD REPORT: API Forge Economy — Economy Evals (Onda 6)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EVALS |
| **Date** | 2026-09-28 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_EVALS.md](./DEFINE_API_FORGE_ECONOMY_EVALS.md) |
| **DESIGN** | [DESIGN_API_FORGE_ECONOMY_EVALS.md](./DESIGN_API_FORGE_ECONOMY_EVALS.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 7/7 |
| **Files Created** | 33 |
| **Files Modified** | 11 |
| **Tests** | 262 passed, 1 skipped (targeted) |
| **Eval** | `evals economy-matrix`: 48 runs, 5/5 gates |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | Contracts | (direct) | ✅ | 5 contracts |
| 2 | Matrix + 16-task corpus + mutants | (direct) | ✅ | |
| 3 | Gate | (direct) | ✅ | |
| 4 | Replay + 4-bundle corpus | (direct) | ✅ | |
| 5 | ROI + information gain | (direct) | ✅ | |
| 6 | Quality floor | (direct) | ✅ | opt-in |
| 7 | Surfaces, tests, docs, SDD chain | (direct) | ✅ | |

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | 44 | Deterministic evals |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
|------|-------|-------|----------|-------|
| `src/apiforge/contracts/economy_evals.py` | ~150 | (direct) | ✅ | |
| `src/apiforge/evals/{matrix,gate,replay}.py` | ~560 | (direct) | ✅ | |
| `src/apiforge/economy/roi.py`, `src/apiforge/runtime/information_gain.py` | ~120 | (direct) | ✅ | |
| `evals/corpus/economy-matrix/*` (16 + README), `evals/corpus/economy-replay/*` (4 + README) | — | (direct) | ✅ | |
| `tests/evals/test_economy_matrix.py` + 5 contract docs | — | (direct) | ✅ | |

---

## Verification Results

### Lint Check

```text
ruff check + ruff format on touched files: clean
```

### Type Check

```text
mypy src/apiforge: Success: no issues found in 417 source files
```

### Tests

| Test | Result |
|------|--------|
| `tests/evals/test_economy_matrix.py` | ✅ 10 |
| `tests/runtime tests/evals tests/mcp tests/contracts tests/economy` | ✅ 262 passed, 1 skipped |

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | Matrix: 9 safety violations per profile — sensitive tasks required a reviewer the catalog could not supply (`task-review` accepted only `read_only`) | `task-review.accepted_risks: [read_only, sensitive]` | small |
| 2 | Ground truth: relaxing `required` on the shared `Order` schema marked compatible | Engine was right (response guarantee weakened) → breaking | small |
| 3 | `list.sort` key using `index()` during sort | Precomputed positions | none |

---

## Autonomous Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Fix the reviewer gap instead of relaxing the safety gate | Safety invariant is non-negotiable |
| 2 | Quality floor opt-in | Defaults and existing routing unchanged |
| 3 | Replay corpus as JSON bundles | `.apiforge/` is gitignored |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| `agent_profiles.yaml` changed | Matrix finding | Sensitive plans now include the reviewer |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Matrix | ✅ | `test_matrix_axes_are_separate_and_gates_pass`, full eval |
| AT-002 | Mutation | ✅ | `test_mutants_flip_compatible_candidates` |
| AT-003 | Gate ship | ✅ | `test_gate_ships_identical_and_rejects_regressions` |
| AT-004 | Gate reject | ✅ | same |
| AT-005 | Replay | ✅ | `test_replay_corpus_keeps_required_roles` |
| AT-006 | ROI | ✅ | `test_runtime_reports_information_gain_and_roi` |
| AT-007 | Info gain | ✅ | `test_information_gain_levels` |
| AT-008 | Quality floor | ✅ | `test_quality_floor_is_a_constraint_and_cost_the_optimization` |
| AT-009 | Invalid report | ✅ | `test_gate_cli_and_mcp_parity` |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Quality per profile | 1.0 | 1.0 / 1.0 / 1.0 | ✅ |
| Safety violations | 0 | 0 | ✅ |
| Mean calls economy ≤ balanced ≤ deep | monotone | 2.56 ≤ 3.00 ≤ 3.44 | ✅ |
| Mutation score | 1.0 | 10/10 | ✅ |

---

## Final Status

### Overall: ✅ COMPLETE

- [x] All tasks from manifest completed
- [x] Targeted verification passes
- [x] Acceptance tests verified
- [ ] Full suite — next step (program end)

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_EVALS.md`
