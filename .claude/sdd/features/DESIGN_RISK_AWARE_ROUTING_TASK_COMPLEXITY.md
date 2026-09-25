# DESIGN: Risk-Aware Routing and Task Complexity

> Technical design for the deterministic, offline-first MVP that makes explicit task risk and complexity shape routing objectives, verification depth and execution composition.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | RISK_AWARE_ROUTING_TASK_COMPLEXITY |
| **Date** | 2026-09-25 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_RISK_AWARE_ROUTING_TASK_COMPLEXITY.md](./DEFINE_RISK_AWARE_ROUTING_TASK_COMPLEXITY.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                 DETERMINISTIC RISK-AWARE ROUTING MVP                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TaskSpec + evidence + local YAML policy                                    │
│                 │                                                            │
│                 ▼                                                            │
│  RoutingRequest normalization ──► RiskComplexityAssessment/v1               │
│                 │                         │                                  │
│                 │                         ├─ objective order                 │
│                 │                         ├─ verification depth              │
│                 │                         ├─ required review roles           │
│                 │                         └─ evidence + unresolved            │
│                 ▼                         ▼                                  │
│  candidate eligibility ─────────► deterministic ranking                      │
│                 │                         │                                  │
│                 └──────────────► RoutingDecision/v1                          │
│                                           │                                  │
│                                           ▼                                  │
│                                  RoutingPlan/v1                              │
│                                           │                                  │
│                ┌──────────────────────────┼─────────────────────────┐        │
│                ▼                          ▼                         ▼        │
│             Runtime                  CLI/TUI                  Governance      │
│          (canonical JSON)       (read-only projection)       (same payload)    │
│                                                                              │
│  All paths are local, versioned, replayable and provider/network-free.       │
└──────────────────────────────────────────────────────────────────────────────┘
```

The assessment is a pure policy result, not a new executor. It is computed once before ranking, attached to the canonical routing decision, and consumed by plan construction and read-only projections. No surface recomputes risk, complexity, eligibility or role composition.

The MVP uses only explicit local inputs: `TaskSpec.risk`, task size, dependencies, expected proofs, required/available evidence, required/available expertise, and the versioned routing policy. Historical scorecards (B) and graph-aware impact analysis (C) remain extension seams and are not required inputs.

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `RiskComplexityAssessment/v1` | Immutable, explainable output of policy classification | Pydantic `VersionedContract` |
| `runtime.risk_complexity` | Pure classifier and stable assessment ID generator | Python, `stable_id`, no I/O |
| Routing normalization | Adds explicit task complexity inputs to `RoutingRequest` | Existing Pydantic routing contracts |
| Routing policy loader | Loads the local risk/complexity rules and validates defaults | `agentic_runtime.yaml` + existing YAML loader |
| Routing decision integration | Computes assessment before eligibility/ranking and preserves its evidence/gaps | Existing `runtime.routing` |
| Plan integration | Applies assessment-derived role and execution effects without changing role disjointness rules | Existing `RoutingPlan` builder |
| Runtime persistence/event | Persists the decision and plan once and emits the same assessment payload | Existing supervisor/store |
| Canonical experience projection | Exposes the persisted result to JSON, CLI, TUI and governance | Existing application projection |
| Evaluation fixtures and gate | Covers golden, holdout, mutation and adversarial cases | pytest + repository eval harness |

## Key Decisions

### Decision 1: Make the assessment the canonical routing explanation

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** Runtime, CLI/TUI and governance need the same explanation for why a task received a routing objective, verification depth and role composition. Recomputing the result in each surface would create semantic drift and break replay equality.

**Choice:** Add an immutable `RiskComplexityAssessment/v1` contract and attach it to `RoutingDecision/v1`. `RoutingPlan/v1` carries the assessment identity and the derived role effects; it does not recalculate the assessment.

**Rationale:** The existing routing decision is already the persisted boundary for candidate assessments, selected capability, fallback order, evidence and unresolved state. An additive field preserves existing contract semantics while making the assessment available to every downstream consumer. A stable assessment ID binds the task revision, policy identity and normalized inputs to one replayable artifact.

**Alternatives Rejected:**
1. A separate unreferenced sidecar - rejected because consumers could select different artifacts or silently omit the assessment.
2. Recompute in the CLI/TUI and governance adapters - rejected because it violates canonical projection parity.

**Consequences:**
- `RoutingDecision/v1` gains an additive optional field and existing fixtures remain valid.
- New consumers must treat assessment evidence and unresolved values as authoritative and must not infer missing state.

### Decision 2: Use a pure policy compiler for MVP classification

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** The MVP must be deterministic, offline and reproducible. The classifier must not depend on model calls, current time, live systems or hidden thresholds.

**Choice:** Implement `assess_risk_complexity(request, policy)` as a pure function. It applies ordered, versioned YAML rules to explicit normalized inputs, returns all matched factors, and preserves missing evidence/expertise as unresolved. Safety risks are policy-controlled gates, not a bypass around evidence checks.

**Rationale:** A policy compiler gives the repository one inspectable source of truth, makes replay fixtures straightforward, and provides a stable seam for future B/C inputs without activating them. It also supports paired fixtures where only risk or an approved complexity input changes.

**Alternatives Rejected:**
1. Historical scorecard inference - deferred to B because it introduces an evidence lifecycle and a new freshness/anti-starvation policy.
2. Graph impact classification - deferred to C because it requires graph completeness, provenance and impact traversal semantics not needed for the MVP.

**Consequences:**
- Initial rule thresholds are explicit in YAML and must be covered by golden, holdout, mutation and adversarial cases.
- Policy changes require a policy version and evaluation updates; the classifier must never silently fall back to an unversioned rule set.

### Decision 3: Preserve `RoutingPlan` role disjointness and bounded fallbacks

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** Risk-aware routing must strengthen review and verification without making the plan an implicit authorization to mutate external state. Existing plan validation prevents duplicate role assignment and unbounded fallbacks.

**Choice:** Assessment effects select objective order, verification depth and required review roles. The existing plan builder remains responsible for primary/fallback/parallel/reviewer/critic/referee placement, role disjointness and `max_fallbacks`. A critical or unresolved assessment can gate the plan while still preserving the proposed composition and gaps.

**Rationale:** Separating policy effects from role allocation keeps the classifier pure and retains the existing safety boundary. It also makes B/C additive: new signals can change an assessment, while the same plan invariants continue to apply.

**Alternatives Rejected:**
1. Let the classifier allocate concrete agent names - rejected because it couples policy classification to candidate availability.
2. Increase fallback counts based on risk - rejected because bounded fallbacks are a safety invariant and the policy may instead require review or refusal.

**Consequences:**
- Some high-risk fixtures may return a non-empty unresolved/gated result without a selected executor.
- Tests must assert both policy effects and existing role invariants.

### Decision 4: Expose only the canonical read-only projection

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** The same assessment must be visible in runtime status, CLI/TUI and governance output without creating a second write path or a surface-specific interpretation.

**Choice:** Extend `ExperienceView.payload` with the persisted assessment, decision and plan summaries. The application projection reads stored artifacts and passes the same structured values to every renderer. Actions remain separate and safe; rendering does not execute routing or change policy state.

**Rationale:** This follows the repository’s existing projection contract and makes parity testable by digesting the canonical payload. It keeps all mutations behind application services and respects the offline-only MVP boundary.

**Alternatives Rejected:**
1. Add routing logic to CLI/TUI - rejected because presentation layers must not add semantics.
2. Create a governance-only summary - rejected because it would permit evidence or unresolved state to diverge from runtime.

**Consequences:**
- Projection schema changes require contract and parity tests.
- TUI formatting may differ, but selected roles, policy identity, evidence and unresolved items must be identical.

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/risk_complexity.py` | Create | Define `RiskComplexityAssessment/v1`, policy effect types and bounded enums | @api-agentic-orchestrator | `contracts/base.py`, `core/ids.py` |
| 2 | `src/apiforge/contracts/routing.py` | Modify | Add normalized task complexity inputs and additive assessment references to routing contracts | @api-agentic-orchestrator | 1 |
| 3 | `src/apiforge/contracts/__init__.py` | Modify | Export the new public contracts | @api-agentic-orchestrator | 1 |
| 4 | `src/apiforge/contracts/registry.py` | Modify | Register `RiskComplexityAssessment/v1` | @api-governance-reviewer | 1 |
| 5 | `src/apiforge/runtime/risk_complexity.py` | Create | Implement pure ordered-rule classifier and stable assessment identity | @api-agentic-orchestrator | 1, 2 |
| 6 | `src/apiforge/runtime/routing.py` | Modify | Load policy effects, classify before ranking, preserve assessment evidence/gaps | @api-agentic-orchestrator | 2, 5 |
| 7 | `src/apiforge/rules/agentic_runtime.yaml` | Modify | Add versioned risk/complexity policy rules and effects | @api-agentic-orchestrator | 1, 5 |
| 8 | `src/apiforge/runtime/supervisor.py` | Modify | Persist assessment-bearing decision/plan and emit canonical routing event | @api-agentic-orchestrator | 5, 6 |
| 9 | `src/apiforge/runtime/runner.py` | Modify | Return persisted routing assessment and plan in runtime status | @api-agentic-orchestrator | 8 |
| 10 | `src/apiforge/contracts/experience.py` | Modify | Add typed projection fields or payload contract for routing explanation | @api-agentic-orchestrator | 1, 8 |
| 11 | `src/apiforge/application/runtime_experience.py` | Modify | Feed stored routing artifacts into the canonical experience view | @api-agentic-orchestrator | 9, 10 |
| 12 | `src/apiforge/application/experience_projection.py` | Modify | Project one canonical assessment/decision/plan payload | @api-agentic-orchestrator | 10, 11 |
| 13 | `src/apiforge/cli_experience.py` | Modify | Render the projection without recomputation or mutation | @api-agentic-orchestrator | 12 |
| 14 | `src/apiforge/tui/app.py` | Modify | Render policy, verification depth, roles, evidence and gaps from projection | @api-agentic-orchestrator | 12 |
| 15 | `docs/contracts/RiskComplexityAssessment-v1.md` | Create | Document fields, provenance, unresolved semantics and compatibility | @api-governance-reviewer | 1, 4 |
| 16 | `docs/contracts/RoutingPolicy-v1.md` | Modify | Document risk/complexity policy rules and evaluation gate | @api-governance-reviewer | 7, 15 |
| 17 | `docs/contracts/RoutingRequest-v1.md` | Modify | Document additive normalized task inputs | @api-governance-reviewer | 2, 15 |
| 18 | `docs/contracts/RoutingDecision-v1.md` | Modify | Document canonical assessment attachment and replay identity | @api-governance-reviewer | 2, 6, 15 |
| 19 | `docs/contracts/RoutingPlan-v1.md` | Modify | Document derived effects, role invariants and gated plans | @api-governance-reviewer | 6, 15 |
| 20 | `tests/contracts/test_risk_complexity.py` | Create | Validate contract enums, immutability, evidence and unresolved invariants | @api-verification-engineer | 1 |
| 21 | `tests/contracts/test_routing.py` | Modify | Cover backward-compatible routing contract behavior | @api-verification-engineer | 2, 6 |
| 22 | `tests/contracts/test_experience.py` | Modify | Validate projection schema and digest-stable payload | @api-verification-engineer | 10, 12 |
| 23 | `tests/runtime/test_risk_complexity.py` | Create | Unit-test rule ordering, paired inputs, gates and stable IDs | @api-verification-engineer | 5, 7 |
| 24 | `tests/runtime/test_routing.py` | Modify | Assert classify-before-rank behavior and existing ranking compatibility | @api-verification-engineer | 6 |
| 25 | `tests/runtime/test_supervisor.py` | Modify | Assert persistence/event parity and no external/provider calls | @api-verification-engineer | 8, 9 |
| 26 | `tests/application/test_runtime_experience.py` | Modify | Verify runtime projection includes canonical artifacts | @api-verification-engineer | 11, 12 |
| 27 | `tests/application/test_experience_parity.py` | Modify | Compare JSON/CLI/TUI/governance projection digests | @api-verification-engineer | 12, 13, 14 |
| 28 | `tests/application/test_cli_experience.py` | Modify | Verify CLI rendering preserves evidence and unresolved diagnostics | @api-verification-engineer | 13 |
| 29 | `tests/tui/test_app.py` | Modify | Verify TUI renders the same policy/role/gap facts | @api-verification-engineer | 14 |
| 30 | `tests/e2e/test_experience_parity.py` | Modify | Exercise end-to-end canonical projection parity | @api-verification-engineer | 8–14 |
| 31 | `tests/fixtures/agentic_runtime/risk_complexity_cases.yaml` | Create | Define golden, paired, unresolved and offline replay fixtures | @api-test-strategist | 5, 6 |
| 32 | `tests/evals/cases/adaptive_routing.yaml` | Modify | Register mandatory MVP risk/complexity evaluation cases | @api-test-strategist | 31 |
| 33 | `tests/evals/test_adaptive_routing_gate.py` | Modify | Enforce golden/holdout/mutation/adversarial coverage and evidence completeness | @api-verification-engineer | 31, 32 |

**Total Files:** 33

## Agent Assignment Rationale

> Agents discovered from `${CLAUDE_PLUGIN_ROOT}/agents/` and matched by file purpose, runtime boundary, contract ownership and testing specialization.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @api-agentic-orchestrator | 1–3, 5–14 | Owns deterministic TaskSpec/routing orchestration, runtime boundaries, persistence and read-only experience integration. |
| @api-governance-reviewer | 4, 15–19 | Owns versioned contract registry, compatibility, refusal semantics and contract documentation. |
| @api-verification-engineer | 20–30, 33 | Independently verifies contracts, persisted artifacts, projection parity, safety boundaries and evaluation gates. |
| @api-test-strategist | 31–32 | Designs fixtures and evaluation matrix, including negative space, mutation and holdout cases. |
| @api-adversarial-critic | Review of 23–25, 32–33 | Challenges hidden fallback, evidence loss, order dependence, policy bypass and false-positive replay claims before build completion. |

**Agent Discovery:**
- Scanned: `.claude/agents/**/*.md` and the project-local specialist catalog.
- Matched by: file type, purpose keywords, API Forge runtime ownership, contract boundaries, KB domains and independent verification needs.
- Confidence: 0.95 for the main assignments because the selected KB patterns and project-local agents both match the proposed work.

## Code Patterns

### Pattern 1: Immutable versioned assessment

```python
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract


class RiskComplexityAssessment(VersionedContract):
    """Pure, replayable explanation of routing policy effects."""

    assessment_id: str
    task_id: str
    revision: int = Field(ge=0)
    policy_id: str
    policy_version: str
    risk: str
    complexity: Literal["simple", "moderate", "complex", "critical"]
    factors: tuple[str, ...] = ()
    objective_order: tuple[Literal["efficiency", "quality"], ...]
    verification_depth: Literal["standard", "elevated", "strict"]
    required_roles: tuple[Literal["reviewer", "critic", "referee"], ...] = ()
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
```

This follows the KB guidance for explicit state/guardrail contracts: unknown and unresolved are represented, not converted into a confident default. The actual implementation should add model validators for unique ordered fields and any `AF-*` refusal metadata required by the repository contract.

### Pattern 2: Pure classification with stable provenance

```python
from apiforge.contracts.risk_complexity import RiskComplexityAssessment
from apiforge.contracts.routing import RoutingPolicy, RoutingRequest
from apiforge.core.ids import stable_id


def assess_risk_complexity(
    request: RoutingRequest,
    policy: RoutingPolicy,
) -> RiskComplexityAssessment:
    """Classify explicit local inputs; do not read time, network or providers."""
    factors = tuple(_matched_factors(request, policy))
    complexity = _complexity_for(request, policy, factors)
    unresolved = tuple(_unresolved_inputs(request, policy))
    assessment_id = stable_id(
        "risk-assessment",
        {
            "task_id": request.task_id,
            "revision": request.revision,
            "policy_id": policy.policy_id,
            "policy_version": policy.policy_version,
            "risk": request.risk,
            "factors": factors,
            "unresolved": unresolved,
        },
    )
    return RiskComplexityAssessment(
        assessment_id=assessment_id,
        task_id=request.task_id,
        revision=request.revision,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        risk=request.risk,
        complexity=complexity,
        factors=factors,
        objective_order=_objectives_for(complexity, policy),
        verification_depth=_verification_for(complexity, policy),
        required_roles=_roles_for(complexity, policy),
        evidence=tuple(request.required_evidence),
        unresolved=unresolved,
    )
```

The implementation must sort or preserve order only where the policy defines order. It must not use unordered sets when they affect IDs, ranking or output order. Missing required evidence/expertise is an unresolved condition and remains visible to the caller.

### Pattern 3: Additive classify-before-rank integration

```python
assessment = assess_risk_complexity(request, policy)
effective_policy = policy.with_objectives(assessment.objective_order)
decision = _rank_eligible(
    request=request,
    policy=effective_policy,
    assessment=assessment,
)
decision = decision.model_copy(
    update={
        "risk_complexity": assessment,
        "evidence": tuple(sorted(set(decision.evidence) | set(assessment.evidence))),
        "unresolved": tuple(sorted(set(decision.unresolved) | set(assessment.unresolved))),
    }
)
```

The concrete implementation should use the repository’s existing immutable model/update conventions. Plan construction consumes `decision.risk_complexity` and applies role effects; it never invokes the classifier a second time.

### Pattern 4: Versioned local policy structure

```yaml
runtime:
  routing:
    policy_version: routing/v1
    objective_order: [efficiency, quality]
    security_mode: gate
    unknown_signal: unresolved
    tie_breaker: capability
    scorecard_update: eval_required
    execution_mode: parallel_review
    max_fallbacks: 1
    risk_complexity:
      policy_version: risk-complexity/v1
      unknown_behavior: unresolved
      risk_overrides:
        sensitive: complex
        external_mutation: critical
        destructive: critical
        irreversible: critical
      ordered_rules:
        - id: missing-required-evidence
          when: required_evidence_unavailable
          complexity: critical
        - id: missing-required-expertise
          when: required_expertise_unavailable
          complexity: complex
        - id: large-task
          when: size_is_L
          complexity: complex
      effects:
        simple: {objectives: [efficiency, quality], verification: standard, roles: []}
        moderate: {objectives: [quality, efficiency], verification: elevated, roles: [reviewer]}
        complex: {objectives: [quality, efficiency], verification: strict, roles: [reviewer, critic]}
        critical: {objectives: [quality], verification: strict, roles: [reviewer, critic, referee]}
```

Rule names, ordering and defaults are policy data and must be validated against the new fixture matrix. The policy loader must reject malformed or duplicate rules rather than silently using a partial policy.

## Data Flow

```text
1. Supervisor loads TaskSpec, local routing YAML and available evidence/capabilities.
   │
   ▼
2. Existing normalization creates RoutingRequest, adding task size, dependencies,
   expected proofs and strategy as explicit immutable inputs.
   │
   ▼
3. Pure classifier applies ordered policy rules and returns RiskComplexityAssessment/v1.
   │     └─ Missing/stale/unresolved inputs remain in unresolved and evidence.
   ▼
4. Eligibility and ranking use the assessment objective order while preserving
   existing candidate signals, tie-breaker, fallback and security gates.
   │
   ▼
5. Supervisor persists one RoutingDecision/v1 and one RoutingPlan/v1, including
   assessment identity, derived effects, evidence and unresolved diagnostics.
   │
   ▼
6. Runtime status and application projection read the persisted artifacts.
   │
   ▼
7. JSON, CLI, TUI and governance render the same canonical facts and digests.
```

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| Local `agentic_runtime.yaml` | Read-only filesystem configuration | None |
| Existing local routing store | Read/write local artifact persistence within the sandbox | None |
| Existing pytest/evaluation fixtures | Read-only test/evaluation inputs | None |
| Provider SDKs, network services and external mutation APIs | No integration in MVP | Not applicable; explicitly prohibited |

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Contract unit | Assessment fields, version, unique ordered values, evidence/unresolved preservation and registry | `tests/contracts/test_risk_complexity.py`, `tests/contracts/test_routing.py` | pytest | 100% of new contract validators and backward-compatibility cases |
| Classifier unit | Rule precedence, risk overrides, paired risk/complexity inputs, deterministic IDs, malformed policy refusal | `tests/runtime/test_risk_complexity.py` | pytest | Every rule, effect and unresolved branch |
| Routing integration | Classify-before-rank, objective changes, role composition, role disjointness and bounded fallbacks | `tests/runtime/test_routing.py` | pytest | All acceptance tests AT-001, AT-002, AT-003, AT-006 |
| Supervisor integration | Persisted decision/plan, event payload, replay equality and offline boundary | `tests/runtime/test_supervisor.py` | pytest + local fakes | AT-001, AT-004, AT-008 |
| Projection parity | Runtime, JSON, CLI, TUI and governance all consume one canonical payload | `tests/application/test_experience_parity.py`, `tests/e2e/test_experience_parity.py` | pytest | AT-005 and evidence/gap preservation |
| Fixture/evaluation gate | Golden, holdout, mutation and adversarial coverage | `tests/fixtures/agentic_runtime/risk_complexity_cases.yaml`, `tests/evals/*` | existing eval runner + pytest | AT-007; gate fails on missing case kind or lost evidence |
| Adversarial review | Conflicting rules, reordered inputs, missing evidence, duplicate roles, unsafe fallback and policy bypass | `@api-adversarial-critic` review of runtime/eval tests | repository review workflow | No silent fallback, drop or authorization |

Required fixture groups:

- Golden: one case for each complexity level and each safety-risk override.
- Paired: identical inputs with only risk or one approved complexity input changed; expected effect is explicit.
- Holdout: unseen combinations of size, dependencies, evidence and expertise.
- Mutation: changed policy rule order, threshold, policy version or evidence availability must alter or gate the result as specified.
- Adversarial: unordered input permutations, missing evidence, unknown signals, duplicate roles and attempts to bypass the security gate.

Each mandatory case records task input, evidence refs, policy version, expected assessment, expected decision/plan effects, projection digest and unresolved diagnostics. The tests compare canonical serialized artifacts rather than presentation text.

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Malformed or duplicate risk/complexity policy rule | Refuse policy load with the repository’s `AF-*` code, rejected field and safe unlock; do not classify with a partial policy | No; human policy correction required |
| Required evidence unavailable or unresolved | Return a visible unresolved assessment and gated/refused routing result preserving evidence refs and refusal details | No automatic retry; resolve evidence or explicitly revise task |
| Required expertise unavailable | Preserve the missing expertise diagnostic and apply only the policy-defined escalation; never pretend a candidate is eligible | No automatic retry; provide expertise or revise task |
| Unknown signal/freshness | Preserve `unknown`/`unresolved` state according to routing policy and prevent a confident fallback | No unless a new local evidence snapshot is supplied |
| Assessment/decision persistence failure | Fail the runtime transition before execution and retain the original error/evidence in the case | Bounded local retry only if existing store policy permits |
| Projection payload missing persisted artifact | Render `UNRESOLVED` with a gap; do not recompute from TaskSpec | No; repair artifact/state and rerun verification |
| Duplicate concrete role in plan | Existing `RoutingPlan` validator rejects the plan | No; deterministic builder/policy fix required |

Every refusal follows the project contract: expose an `AF-*` code, rejected field and safe unlock, and ensure the code is present in `docs/catalog-contract.md`. No error handler may hide a critical finding to save output space.

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `runtime.routing.risk_complexity.policy_version` | string | `risk-complexity/v1` | Version of the local classification policy included in replay identity |
| `runtime.routing.risk_complexity.unknown_behavior` | enum | `unresolved` | Handling for unknown or unavailable inputs; MVP permits unresolved only |
| `runtime.routing.risk_complexity.risk_overrides` | mapping | see YAML | Explicit risk-to-complexity escalation for safety-sensitive tasks |
| `runtime.routing.risk_complexity.ordered_rules` | list | see YAML | Deterministic ordered predicates for approved complexity inputs |
| `runtime.routing.risk_complexity.effects` | mapping | see YAML | Objective order, verification depth and required review roles per complexity |
| `runtime.routing.max_fallbacks` | integer | `1` | Existing bound retained for every assessed plan |
| `runtime.routing.security_mode` | enum | `gate` | Existing security gate; assessment cannot weaken it |

Policy loading must produce a typed versioned policy object. Defaults may only be used where the existing contract explicitly defines them; new risk/complexity rules must be present and versioned in the local YAML so replay does not depend on code defaults.

## Security Considerations

- Risk classification is advisory policy state and never authorizes external mutation, destructive work, automatic approval or a policy bypass.
- `external_mutation`, `destructive` and `irreversible` risks are gate-controlled and escalate review; unresolved evidence remains unresolved.
- Evidence refs, refusal codes, rejected fields and safe unlocks are preserved end-to-end and are not replaced by a short summary.
- Inputs are normalized and validated before entering stable IDs; unordered collections must not create nondeterministic decisions.
- The classifier performs no provider SDK, network, database or live external call. Runtime proof remains fixture-scoped and local.
- Assessment and plan roles remain disjoint, and fallback counts remain bounded by the existing contract validator.
- B and C extension seams accept new evidence through explicit versioned inputs and cannot silently activate historical or graph-derived behavior.

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Existing structured routing event includes assessment ID, policy ID/version, complexity, matched factor IDs, verification depth, required roles, evidence refs and unresolved diagnostics. Never log secrets or raw sensitive task inputs. |
| Metrics | Local/evaluation counters for assessment complexity distribution, gated/unresolved outcomes, evidence-preservation failures, projection parity failures and eval-case coverage. No production throughput claim is inferred. |
| Tracing | Reuse existing runtime event/case receipts; link `assessment_id`, `decision_id`, `plan_id` and projection digest. Record policy/ruleset version and command/test result in the case. |

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-25 | design-agent | Initial architecture for MVP A; B scorecard-adaptive and C graph-aware impact are explicit deferred extension seams |

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_RISK_AWARE_ROUTING_TASK_COMPLEXITY.md`
