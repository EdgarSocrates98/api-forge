# DESIGN: API Forge Economy — Economy Evals (Onda 6)

> Deterministic multi-axis matrix, evaluation gate, replay, ROI, information gain and an opt-in quality floor.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EVALS |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_EVALS.md](./DEFINE_API_FORGE_ECONOMY_EVALS.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
evals/corpus/economy-matrix/<task>.yaml  {protocol, baseline, candidate, expected, holdout, mutants}
        │
        ▼ per task
deterministic verdict  (openapi.diff_contracts | grpc.compatibility.compare)   ── L0 evidence ids
        │ risk: breaking → sensitive/M, compatible → read_only/S
        ▼ per profile economy|balanced|deep
runtime run (fake adapter, temp root)  ── routing-plan, economy block, role context
        ▼
MatrixRow {quality{verdict_ok, safety_ok}, evidence{ids}, cost{calls, invocations, fanout, trimmed},
           context{role_bytes, evidence_bytes}, latency{ms}}          (no blended score)
        ▼
EconomyMatrix/v1 report ── gates: quality 1.0 per profile, safety 0 regressions, cost monotone,
                                   mutation score 1.0, holdout pass
evals gate  A.json B.json → EvaluationGate/v1 {decision ship|reject, regressions, savings}
evals replay --root R | --corpus C → ReplayReport/v1 (stored decision → rebuilt plan → current policy)
economy roi --root R → RoleROI/v1 rows (calls, facts_added, unresolved_added, outcome_changed)
supervisor economy block + information_gain {level, reason}
ScorecardRoutingPolicy.quality_floor (opt-in): below → unresolved lane; champions by observed cost
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `contracts/economy_evals.py` | MatrixRow, EconomyMatrix, EvaluationGate, ReplayRun, ReplayReport, RoleROI, InformationGain | pydantic |
| `evals/matrix.py` | Tasks, verdicts, mutants, runs, axes, gates | runtime + diff |
| `evals/gate.py` | Report comparison | pure |
| `evals/replay.py` | Re-plan stored decisions | routing + economy |
| `economy/roi.py` | Role ROI from stored runs | json |
| `runtime/information_gain.py` | Gain level from artifacts | pure |
| `runtime/scorecard_routing.py`, `contracts/scorecard_routing.py` | quality floor | existing |
| CLI/MCP | `evals economy-matrix|gate|replay`, `economy roi` | typer |

---

## Key Decisions

### Decision 1: Quality = deterministic verdict + safety invariant

Verdict: breaking if any `AF-BREAKING-*` change (OpenAPI) or verdict `breaking` (gRPC); `unresolved` if only unclassified changes. Safety: every role in `EconomyPlan.minimum_roles` is present in the executed routing plan. Both are booleans; a run passes quality only if both hold.

### Decision 2: Axes never blended

Report holds per-profile aggregates per axis; gates are per axis.

### Decision 3: Mutants are structural edits

`remove_operation`, `remove_response_property`, `add_required_request_property`, `remove_response_status` applied to compatible candidates; each must turn the verdict to breaking.

### Decision 4: Replay rebuilds the pre-economy plan

Stored `routing.json` (decision without economy) → `build_routing_plan` → `build_economy_plan` + `apply_economy` with current policy and requested profile → compare with stored `economy.json`/`routing-plan.json`. Replay corpus = flat JSON bundles generated from matrix runs (committed), plus `--root` scanning live runs.

### Decision 5: Quality floor is opt-in

`quality_floor: float | None = None`; when set: scorecard below floor → lane `unresolved` (`quality-below-floor`); champions sorted by `observed_cost` ascending (unknown cost last), ties by inherited order.

### Decision 6: Information gain is reported, not a new stop

`low` when artifacts agree, no unresolved and min confidence ≥ threshold; `high` when they disagree or unresolved exist; else `medium`. The existing escalation triggers stay authoritative; the level explains them.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `contracts/economy_evals.py` + registry | Create | Contracts | @python-developer | — |
| 2 | `evals/matrix.py` + `evals/corpus/economy-matrix/*` | Create | Matrix | @test-generator | 1 |
| 3 | `evals/gate.py`, `evals/replay.py`, `evals/corpus/economy-replay/*` | Create | Gate/replay | @python-developer | 2 |
| 4 | `economy/roi.py` | Create | ROI | @python-developer | 1 |
| 5 | `runtime/information_gain.py`, `runtime/supervisor.py` | Create/Modify | Info gain | @python-developer | 1 |
| 6 | `contracts/scorecard_routing.py`, `runtime/scorecard_routing.py` | Modify | Floor | @python-developer | — |
| 7 | CLI/MCP, tests, docs, SDD chain | Create/Modify | Surfaces | @python-developer | all |

---

## Agent Assignment Rationale

Executed inline.

---

## Code Patterns

```python
def verdict(changes) -> str:
    if any(c.breaking for c in changes): return "breaking"
    if any(c.code.value in UNRESOLVED for c in changes): return "unresolved"
    return "compatible"
```

---

## Data Flow

Corpus → verdict + mutants → runs per profile → rows → report → gates. Gate reads two reports. Replay reads stored decisions. ROI reads stored run artifacts.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| None | offline | — |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | verdicts, mutants, gate, info gain, quality floor | `tests/evals/test_economy_matrix.py` | pytest | AT-002–004, 007–009 |
| Integration | matrix subset, replay, ROI | same | pytest | AT-001, 005, 006 |
| Eval | full matrix | `evals economy-matrix` | CLI | DEFINE criteria |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Bad report file | `AF-EVALS-GATE-INVALID` | No |
| Reports over different cases | `AF-EVALS-GATE-MISMATCH` | No |
| Stored run without decision | `AF-REPLAY-RUN-INCOMPLETE` (row unresolved, never guessed) | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `--max-quality-regression` | int | 0 | Gate tolerance (safety always 0) |
| `quality_floor` | float | None | Opt-in routing floor |

---

## Security Considerations

- Offline, fake adapter; replay never calls providers.

---

## Observability

- Report JSON per axis; gate reasons name each regressed case.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_EVALS.md`
