# DESIGN: Scorecard-Adaptive Routing

> Technical design for a deterministic champion/challenger policy backed by local, fresh and evidence-gated scorecards.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | SCORECARD_ADAPTIVE_ROUTING |
| **Date** | 2026-09-25 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_SCORECARD_ADAPTIVE_ROUTING.md](./DEFINE_SCORECARD_ADAPTIVE_ROUTING.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────┐
│                 SCORECARD-ADAPTIVE ROUTING                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ RoutingRequest + local scorecard snapshots + YAML policy        │
│                         │                                        │
│                         ▼                                        │
│              [Pure scorecard assessor]                           │
│          fresh promoted → champion                               │
│          eligible unknown → challenger                            │
│          stale/unresolved → unresolved                            │
│                         │                                        │
│                         ▼                                        │
│ [Risk/complexity objective ranking] → [lane ordering + bound]    │
│                         │                                        │
│                         ▼                                        │
│ RoutingDecision/v1 + ScorecardRoutingAssessment/v1               │
│                         │                                        │
│                         ▼                                        │
│ RoutingPlan/v1 + existing read-only runtime/CLI/TUI projections  │
│                                                                  │
│ No provider call, live telemetry, automatic promotion or write   │
│ outside the local routing artifacts.                             │
└──────────────────────────────────────────────────────────────────┘
```

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `ScorecardRoutingPolicy/v1` | Versions champion eligibility, freshness treatment and challenger bound | Pydantic contract + local YAML |
| `ScorecardCandidateAssessment/v1` | Explains one candidate's lane, history, freshness, evidence and gaps | Frozen Pydantic model |
| `ScorecardRoutingAssessment/v1` | Canonical ordered lane result and adaptive replay identity | Frozen Pydantic model |
| Pure scorecard assessor | Classifies and orders candidates without side effects | Typed Python transformation |
| Routing integration | Applies adaptive lane ordering after inherited risk/complexity ranking | Existing routing runtime |
| Canonical persistence/projection | Embeds assessment in decision and challenge metadata in plan | Existing store and projections |
| Local eval matrix | Covers replay, champion preference, challenger bound, freshness and mutation | Pytest + YAML fixtures |

## Key Decisions

### Decision 1: Additive canonical assessment at the routing boundary

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** The runtime already persists one `RoutingDecision/v1`, and all read-only surfaces consume that artifact. A second adaptive store would invite drift.

**Choice:** Add `scorecard_routing: ScorecardRoutingAssessment | None` to `RoutingDecision/v1` and add bounded `challenger_order` metadata to `RoutingPlan/v1`.

**Rationale:** The nested assessment keeps policy identity, lane decisions, scorecard refs and unresolved state in the same stable decision hash. The plan records the challenge opportunity without treating it as an implicit execution side effect.

**Alternatives Rejected:**
1. A mutable sidecar route file - rejected because projections could recompute different lane decisions.
2. Reusing only `CandidateAssessment.ranking_key` - rejected because it cannot preserve lane, freshness and gap provenance.

**Consequences:**
- Existing contracts remain compatible because fields are optional/additive.
- Consumers must preserve the nested assessment when serializing routing decisions.

---

### Decision 2: Lexicographic champion/challenger lanes, not a weighted scalar

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** A single weighted score can conceal freshness and evidence failures and can starve candidates with no history.

**Choice:** First rank eligible candidates using the inherited risk/complexity objective order; then place fresh promoted champions first, bounded challengers next, and unresolved history last. When no champion exists, the first bounded challenger preserves the inherited ranking order.

**Rationale:** This is an explicit policy state machine: evidence gates lane eligibility, existing objective ranking orders candidates within a lane, and a small challenger bound provides deterministic exploration.

**Alternatives Rejected:**
1. Weighted quality/cost/duration scalar - rejected because policy reasoning becomes opaque and freshness becomes a penalty rather than a gate.
2. Unknown candidates always last - rejected because new implementations could never acquire verified evidence.

**Consequences:**
- Challenger selection is bounded and explainable, but it is not proof of superiority.
- Live shadow comparison remains a future governed feature.

---

### Decision 3: Stale and unresolved history is visible but never champion evidence

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** Existing scorecards expose freshness state and gaps; silently treating stale data as current would violate the evidence contract.

**Choice:** A candidate is champion-eligible only when it has a scorecard with promoted quality, the configured minimum evaluation history, minimum quality threshold, and `fresh` freshness. Stale, unresolved or unknown freshness produces explicit diagnostics and cannot authorize champion status.

**Rationale:** This follows the guardrail and evaluation KB patterns: validation happens before selection, and missing evidence remains observable rather than being coerced into a confident value.

**Alternatives Rejected:**
1. Treat stale quality as a normal observed signal - rejected because it can dominate current candidates after expiry.
2. Drop stale candidates entirely - rejected because eligibility and historical evidence are separate concerns; the route must preserve the diagnostic.

**Consequences:** Stale/unresolved candidates may remain in the base eligible trace, but adaptive lane metadata prevents them from being treated as champions.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/scorecard_routing.py` | Create | Versioned adaptive policy and assessment contracts | @python-developer | None |
| 2 | `src/apiforge/contracts/routing.py` | Modify | Add optional adaptive assessment and plan challenge metadata | @python-developer | 1 |
| 3 | `src/apiforge/contracts/registry.py` | Modify | Register new v1 contracts | @python-developer | 1 |
| 4 | `src/apiforge/contracts/__init__.py` | Modify | Export new contract types | @python-developer | 1 |
| 5 | `src/apiforge/runtime/scorecard_routing.py` | Create | Pure lane classifier and deterministic adaptive ordering | @python-developer | 1 |
| 6 | `src/apiforge/runtime/routing.py` | Modify | Load policy, apply adaptive assessment and persist evidence | @python-developer | 2, 5 |
| 7 | `src/apiforge/rules/agentic_runtime.yaml` | Modify | Declare scorecard adaptation policy defaults | (general) | 1, 6 |
| 8 | `docs/contracts/ScorecardRoutingAssessment-v1.md` | Create | Document adaptive contract and lane semantics | (general) | 1 |
| 9 | `docs/contracts/RoutingDecision-v1.md` | Modify | Document nested scorecard assessment | (general) | 2, 8 |
| 10 | `docs/contracts/RoutingPlan-v1.md` | Modify | Document bounded challenge metadata | (general) | 2 |
| 11 | `docs/contracts/RoutingPolicy-v1.md` | Modify | Document scorecard adaptation policy | (general) | 7 |
| 12 | `tests/contracts/test_scorecard_routing.py` | Create | Contract registration and validator tests | @test-generator | 1, 3 |
| 13 | `tests/contracts/test_routing.py` | Modify | Additive routing compatibility coverage | @test-generator | 2 |
| 14 | `tests/runtime/test_scorecard_routing.py` | Create | Lane, freshness, bound and replay tests | @test-generator | 5, 6 |
| 15 | `tests/runtime/test_routing.py` | Modify | Existing routing and adaptive integration coverage | @test-generator | 6 |
| 16 | `tests/runtime/test_routing_plan.py` | Modify | Plan challenge metadata and ID stability | @test-generator | 2, 6 |
| 17 | `tests/fixtures/agentic_runtime/scorecard_adaptive_cases.yaml` | Create | Local golden/holdout/mutation/adversarial cases | @test-generator | 5 |
| 18 | `tests/evals/cases/scorecard_adaptive_routing.yaml` | Create | Mandatory adaptive evaluation matrix | @test-generator | 17 |
| 19 | `tests/evals/test_scorecard_adaptive_routing_gate.py` | Create | Eval gate runner for all mandatory case kinds | @test-generator | 18 |

**Total Files:** 19

## Agent Assignment Rationale

> Agents discovered from `${CLAUDE_PLUGIN_ROOT}/agents/**/*.md` - Build phase invokes matched specialists.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1–6 | Typed Python contracts and pure routing integration |
| @test-generator | 12–19 | Pytest fixtures, contract cases and evaluation gates |
| (general) | 7–11 | YAML and Markdown artifacts follow existing repository conventions |

**Agent Discovery:**
- Scanned: `${CLAUDE_PLUGIN_ROOT}/agents/**/*.md`
- Matched by: Python contract/runtime purpose, test/evaluation purpose and local policy/documentation paths
- Execution note: the current Codex surface exposes no Task delegation tool; build will execute these assignments directly and record that decision.

## Code Patterns

### Pattern 1: Frozen versioned assessment

```python
class ScorecardRoutingAssessment(VersionedContract):
    assessment_id: str
    policy_version: str
    candidates: tuple[ScorecardCandidateAssessment, ...] = ()
    champion_order: tuple[str, ...] = ()
    challenger_order: tuple[str, ...] = ()
    selected_challengers: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
```

The assessment is immutable, closed and serialized inside the canonical decision.

### Pattern 2: Pure lane classification

```python
def classify_lane(
    scorecard: AgentScorecard | None,
    *,
    eligible: bool,
    policy: ScorecardRoutingPolicy,
) -> tuple[ScorecardLane, tuple[str, ...]]:
    if not eligible:
        return "unresolved", ("candidate-ineligible",)
    if scorecard is None:
        return "challenger", ("scorecard-missing",)
    if scorecard.freshness_state in {"stale", "unresolved"}:
        return "unresolved", (f"scorecard-{scorecard.freshness_state}",)
    if not scorecard.quality_promoted:
        return "challenger", ("quality-not-promoted",)
    if scorecard.evaluation_count < policy.min_evaluations:
        return "challenger", ("insufficient-evaluations",)
    if scorecard.quality_score < policy.min_quality_score:
        return "challenger", ("quality-below-threshold",)
    return "champion", ("fresh-promoted-scorecard",)
```

This pattern adapts the KB's guardrail and functional-transformation guidance: validate the boundary first, then return explicit state rather than a hidden numeric penalty.

### Pattern 3: Versioned local policy

```yaml
scorecard_adaptation:
  policy_version: scorecard-routing/v1
  min_evaluations: 1
  min_quality_score: 0.0
  challenger_slots: 1
  require_quality_promoted: true
  stale_behavior: unresolved
```

Malformed policy is refused with `AF-RUNTIME-POLICY`; no partial defaults are applied.

### Pattern 4: Fixture-driven replay

```python
first = route_capabilities(..., scorecards=scorecards)
second = route_capabilities(..., scorecards=tuple(reversed(scorecards)))
assert first.decision_id == second.decision_id
assert first.scorecard_routing == second.scorecard_routing
```

Input collections are canonicalized before the stable ID is computed, following the testing KB's ordering and boundary guidance.

## Data Flow

```text
1. Supervisor loads local RoutingRequest, capability profiles and scorecard snapshots.
   │
   ▼
2. A's risk/complexity assessment derives objective order and required roles.
   │
   ▼
3. Existing eligibility and objective ranking produce the base candidate order.
   │
   ▼
4. Pure scorecard assessor classifies each candidate as champion, challenger or unresolved.
   │     └─ Fresh promoted history can champion; stale/unresolved history remains visible.
   │
   ▼
5. Adaptive order groups champions, bounded challengers and remaining candidates.
   │
   ▼
6. RoutingDecision persists assessment ID, policy, lane details, refs and gaps.
   │
   ▼
7. RoutingPlan persists bounded challenger metadata; existing runtime execution roles remain unchanged.
```

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Local `.apiforge/scorecards/*.json` | Read-only local snapshot input | None |
| Local `agentic_runtime.yaml` | Read-only policy configuration | None |
| Existing routing store/projections | Local read/write canonical artifacts | None |
| Provider SDKs, network, live database and external mutation APIs | Explicitly not integrated | Not applicable |

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Contract unit | Lane literals, policy bounds, assessment consistency, registry | `tests/contracts/test_scorecard_routing.py`, `tests/contracts/test_routing.py` | pytest | Every validator and compatibility path |
| Classifier unit | Champion/challenger/unresolved, freshness, threshold, ordering and permutation replay | `tests/runtime/test_scorecard_routing.py` | pytest | Every lane and reason code |
| Routing integration | Adaptive ordering after risk/complexity, role separation and legacy behavior | `tests/runtime/test_routing.py`, `tests/runtime/test_routing_plan.py` | pytest | AT-001 through AT-006 |
| Feedback regression | Existing evidence-gated scorecard update remains unchanged | `tests/runtime/test_feedback.py` | pytest | AT-007 |
| Evaluation gate | Golden, holdout, mutation and adversarial matrix | `tests/fixtures/agentic_runtime/scorecard_adaptive_cases.yaml`, `tests/evals/*` | pytest + local gate | AT-008 and mandatory case kinds |
| Static validation | Formatting and types | Changed Python files | Ruff + mypy | No new lint/type errors |

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Malformed scorecard policy | Refuse with `AF-RUNTIME-POLICY`, rejected field and unlock; do not route with partial policy | No; correct local policy |
| Invalid scorecard snapshot | Existing loader raises `AF-SCORECARD-INVALID`; preserve the path and stop adaptive classification | No automatic retry |
| Stale/unresolved scorecard | Emit unresolved lane and freshness gap; never mark champion | Only with a new local snapshot |
| Missing scorecard | Keep eligible candidate in challenger lane with explicit reason | No; bounded challenge is deterministic |
| No eligible candidate | Preserve existing `AF-CAPABILITY-ELIGIBILITY` refusal and adaptive unresolved evidence | No; provide evidence/profile |
| Duplicate candidate or lane order | Canonical builder de-duplicates by capability and contract validation rejects invalid duplicates | No; fix policy/builder |
| Feedback gate not PASS | Reuse existing blocked/not-updated behavior; do not persist promotion | No automatic retry |

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `runtime.routing.scorecard_adaptation.policy_version` | string | `scorecard-routing/v1` | Policy identity included in replay |
| `runtime.routing.scorecard_adaptation.min_evaluations` | integer | `1` | Minimum passed history for champion eligibility |
| `runtime.routing.scorecard_adaptation.min_quality_score` | float | `0.0` | Minimum promoted quality score |
| `runtime.routing.scorecard_adaptation.challenger_slots` | integer | `1` | Maximum selected challenger candidates |
| `runtime.routing.scorecard_adaptation.require_quality_promoted` | boolean | `true` | Requires evidence-gated promotion |
| `runtime.routing.scorecard_adaptation.stale_behavior` | enum | `unresolved` | Stale/unresolved history treatment; MVP only permits explicit unresolved |

## Security Considerations

- Scorecards are advisory routing evidence and never authorize external mutation or policy bypass.
- Stale, unresolved, unpromoted and malformed history cannot silently become champion evidence.
- Evidence refs, evaluation refs, freshness state, reasons and gaps are preserved in canonical artifacts.
- Challenger selection is bounded by local policy and cannot expand runtime budgets or fallback limits.
- No provider SDK, network, database or clock dependency is introduced.
- Existing risk/complexity security gates and required roles remain authoritative.

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Existing routing trace gains policy version, lane, scorecard profile, freshness and reason data without raw task secrets |
| Metrics | Local/evaluation counters for champion, challenger, unresolved and starvation-prevention outcomes; no production performance claim |
| Tracing | Stable `scorecard_assessment_id`, `decision_id`, `plan_id`, scorecard refs and policy version are persisted in replay artifacts |

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-25 | design-agent | Initial architecture for deterministic scorecard-adaptive routing B |
| 1.1 | 2026-09-25 | ship-agent | Archived after implementation, evaluation and independent verification |

## Next Step

**Archived.** Use this design as the baseline for future shadow/promotion extensions.
