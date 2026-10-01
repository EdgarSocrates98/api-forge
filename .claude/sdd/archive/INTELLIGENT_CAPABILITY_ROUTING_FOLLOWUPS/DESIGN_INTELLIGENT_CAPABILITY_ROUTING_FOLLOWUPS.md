# DESIGN: Intelligent Capability Routing Follow-ups

> Technical design for implementing the evidence-gated foundation of the Intelligent Capability Routing follow-up program.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS |
| **Date** | 2026-09-24 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md](./DEFINE_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md) |
| **Status** | ✅ Shipped |

The build handoff in this design is intentionally limited to **Wave 0**. Waves 1–5 are designed as sealed extension points and must not be promoted or implemented as one unbounded change.

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│             INTELLIGENT CAPABILITY ROUTING — EVOLUTION CONTROL PLANE         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [TaskSpec + Policy]                                                        │
│          │                                                                  │
│          ▼                                                                  │
│  [Evolution Coordinator] ── loads ──> [Local Knowledge / Receipts]           │
│          │                                  │                                │
│          ▼                                  ▼                                │
│  [Deterministic Router] ─────────────> [Evidence Coverage]                   │
│          │                                  │                                │
│          ├── local/replay ───────────────┐  │                                │
│          ├── shadow ────────────────────┤  ▼                                │
│          └── external-read boundary ────┘ [Promotion Gate]                   │
│                                             │                                 │
│                         ┌───────────────────┴──────────────────┐              │
│                         ▼                                      ▼              │
│                   [ACTIVE]                              [FALLBACK/BLOCKED]   │
│                         │                                      │              │
│                         └──────────────┬───────────────────────┘              │
│                                        ▼                                      │
│                         [Append-only RunStore + Trace]                       │
│                                        │                                      │
│                         ┌──────────────┴──────────────┐                       │
│                         ▼                             ▼                       │
│                   [CLI/TUI projection]       [CI/workflow receipt]             │
│                                                                             │
│  Future sealed waves:                                                       │
│  Knowledge Packs → complexity/DAG → offline/shadow optimizer → CLI/TUI/matrix│
│  → external GitHub governance. No wave bypasses the Promotion Gate.         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Design confidence:** high. The topology combines KB-backed evaluation, guardrails, observability, clean architecture and integration-test patterns with existing `RoutingDecision`, `FreshnessResult`, `ExternalReadReceipt`, `TaskPlan`, `RunStore` and runtime-gate implementations.

### Layering rule

```text
contracts  ←  runtime/application  ←  integrations/surfaces
    ↑                 ↑                         ↑
 immutable data   deterministic policy     read-only or workflow boundary
```

Contracts contain no I/O or provider calls. Runtime/application code consumes contracts and policies, but does not acquire external authority. Integrations produce observations and receipts. CLI/TUI/CI project state; they do not reimplement routing decisions.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Evolution contracts | Represent wave, mode, evidence, coverage, promotion and fallback state as closed immutable models | Pydantic v2 `VersionedContract` |
| Evolution coordinator | Orchestrate the bounded sequence from request to evidence gate without widening scope | Existing Python runtime/application services |
| Evidence Coverage evaluator | Calculate explainable coverage over required evidence and decision claims; preserve missing/unknown/unresolved states | Pure Python, Pydantic contracts, deterministic rules |
| Promotion gate | Decide `planned`, `observed`, `simulated`, `active` or `blocked` from mode, policy, evidence and evaluation result | Pure Python policy service |
| Deterministic router | Reuse current eligibility/ranking, attach evolution mode and preserve static fallback | `src/apiforge/runtime/routing.py` |
| RunStore extension | Persist evolution decision, coverage, gate result and fallback alongside current run/routing artifacts | Append-only JSON/JSONL filesystem store |
| Knowledge/freshness boundary | Reuse local pack loader and freshness verification; never fetch or rewrite knowledge in the core | Existing loader/freshness modules plus future read-only adapters |
| Adaptive planner boundary | Future bounded estimator and DAG candidate compiler; Wave 0 exposes only the contract seam and static fallback | TaskSpec/TaskPlan-compatible Python service |
| Optimizer boundary | Future offline/shadow weight and bandit evaluation; no online promotion in Wave 0 | Isolated evaluator with immutable baseline |
| Provider boundary | Future capability discovery and execution observations with receipts; no provider SDK in `src/` | Injected protocol and external host adapter |
| Operational projections | Future CLI modules and TUI views consume shared snapshots and unresolved gaps | Typer, Textual/Rich/JSON fallback |
| Governance boundary | Future GitHub state is read-only to core; authorized mutations remain in dedicated workflow/host | Existing GitHub adapter, `scripts/github_pr_host.py`, CI workflows |

### Wave boundaries

| Wave | Delivered capability | Entry gate | Exit proof |
|------|----------------------|------------|------------|
| 0 | Evidence-gated evolution state, modes, coverage skeleton, promotion and fallback | Existing routing contracts and local fixtures are available | Replayable gate decisions with persisted traces and no unauthorized promotion |
| 1 | Knowledge Packs, freshness policy and provider/model capability receipts | Wave 0 receipts and unresolved semantics pass | Versioned pack/receipt evidence; provider claims remain bounded |
| 2 | Complexity estimator and bounded adaptive DAG | Evidence Coverage explains the required decision inputs | Static/adaptive comparison with dependency, budget and rollback proof |
| 3 | Offline weights and shadow bandit | Frozen baseline, holdout and mutation gate | Promotion or rejection of candidate weights with rollback artifact |
| 4 | CLI/TUI modular projections and expanded Python matrix | Shared contracts stable | Surface parity and observed environment receipts |
| 5 | External GitHub governance integration | Workflow and least-privilege policy independently configured | External governance receipt; core remains read-only |

---

## Key Decisions

### Decision 1: Evidence-gated state machine before optimization

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** The program has local traces and scorecards but no sufficient external telemetry for online learning. A route that looks efficient can still be unsafe, stale or unsupported.

**Choice:** Implement a closed promotion state machine with explicit modes: `local`, `replay`, `shadow` and `external-read`; promotion states are `planned`, `observed`, `simulated`, `active` and `blocked`. `active` requires evidence references, a gate result, a fallback and a reversible policy.

**Rationale:** This directly applies the evaluation-framework and guardrail patterns: structured evidence, explicit failure states, defense-in-depth and independent quality gates. It also makes the existing `RoutingDecision.unresolved` semantics reusable rather than replacing them with a confidence guess.

**Alternatives Rejected:**

1. Online bandit first — rejected because there is no frozen baseline and independent holdout evidence yet.
2. Implicit mode inferred from adapter presence — rejected because capability presence is not authorization or execution proof.

**Consequences:**

- Every future optimization path carries additional gate metadata and cannot silently become active.
- Wave 0 delivers control-plane value before provider integrations exist.
- Operators see `blocked` or fallback states more often when evidence is incomplete; this is intentional and must remain visible.

---

### Decision 2: Contract-first, additive versioning

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** Existing contracts are frozen, closed and versioned. In-place shape changes would break replay and historic artifacts.

**Choice:** Add sibling contract models or additive optional fields only when compatible; use Pydantic `VersionedContract`, `extra="forbid"`, immutable tuples and cross-field validators. Every persisted artifact identifies its policy and contract version.

**Rationale:** This follows the local Pydantic and clean-architecture patterns and preserves replayability. Schema evolution must be explicit, not inferred from untyped dictionaries.

**Alternatives Rejected:**

1. Untyped JSON extension fields — rejected because they hide unsupported states and weaken the contract gate.
2. Mutable shared dictionaries — rejected because they make traces non-reproducible and can blur observed versus inferred evidence.

**Consequences:**

- New waves may add contracts without invalidating Wave 0 artifacts.
- Design and build must maintain schema fixtures and explicit migration/compatibility tests.

---

### Decision 3: Static plan is the mandatory safety fallback

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** Complexity estimation and adaptive DAG selection are intentionally deferred, but the future design must not create a second uncontrolled execution engine.

**Choice:** Adaptive planning produces a candidate `TaskPlan`/DAG. If validation, evidence, dependencies, budget or policy checks fail, the coordinator returns the current deterministic/static plan with an explicit gap.

**Rationale:** The Airflow DAG patterns emphasize idempotency, atomic tasks and observable retries; the project already has `TaskSpec`, `TaskPlan`, budgets and rollback. Treating adaptation as a bounded proposal keeps those invariants in the existing plan compiler.

**Alternatives Rejected:**

1. Let the estimator directly execute tasks — rejected because estimation would gain authority over execution.
2. Generate a free-form graph in the CLI/TUI — rejected because surfaces must remain projections, not domain owners.

**Consequences:**

- Adaptive DAG work can be tested by comparing plans before enabling execution.
- Some apparently beneficial adaptations will be rejected until their evidence is complete.

---

### Decision 4: External systems are observations or dedicated workflow mutations

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** Provider capability, freshness, GitHub branch protection and governance state live outside the local deterministic core.

**Choice:** Provider/GitHub adapters expose read-only protocols and receipts. Any allowed GitHub mutation remains in the existing dedicated workflow/host boundary with least-privilege credentials. The core records limitations instead of inferring permissions, deployment safety or authorship.

**Rationale:** This preserves the `ExternalReadReceipt` and `GitHubPrReceipt` boundaries already present in the repository and follows the project operating contract.

**Alternatives Rejected:**

1. Import provider SDKs into `src/` — rejected by the local-first and dependency boundary.
2. Let an agent call GitHub directly — rejected because authorization and mutation ownership must remain with the workflow boundary.

**Consequences:**

- A receipt can prove correspondence/freshness of an observation, but not authorship or production safety.
- External claims may remain `unresolved` until a dedicated receipt exists.

---

### Decision 5: Wave 0 build is deliberately finite

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** The brainstorm covers nine deferred areas. Implementing all of them in one build would create an unreviewable change and make independent verification impossible.

**Choice:** The current build manifest contains only Wave 0: contracts, Evidence Coverage foundation, promotion gate, modes, persistence, fixtures and tests. Each later wave has entry/exit gates and must be opened by a follow-up design/iterate step.

**Rationale:** This is the smallest reversible slice that makes the remaining work governable. It also keeps the first build compatible with the project’s sandbox and evidence rules.

**Alternatives Rejected:**

1. List every future source file in the current build — rejected because it would imply authorization to implement all waves now.
2. Deliver documentation only — rejected because Wave 0 needs executable contracts and gate tests to prove the roadmap’s foundation.

**Consequences:**

- `/build` should implement Wave 0 only.
- Later waves retain a clear place in the architecture but remain unresolved until their gates are satisfied.

---

## File Manifest

The following **Wave 0** files are the only files authorized by this design’s build handoff.

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/routing_evolution.py` | Create | Closed contracts for evolution mode, promotion state, gate result and coverage summary | `@genai-architect` | Existing `VersionedContract`, `EvidenceRecord` |
| 2 | `src/apiforge/contracts/evidence.py` | Modify | Add only the additive primitives needed to reference coverage and promotion evidence | `@data-quality-analyst` | 1 |
| 3 | `src/apiforge/contracts/knowledge.py` | Modify | Preserve pack/freshness semantics used by Wave 0 without introducing network reads | `@data-quality-analyst` | Existing pack contracts |
| 4 | `src/apiforge/contracts/__init__.py` | Modify | Export the new versioned contracts through the canonical package surface | `@python-developer` | 1 |
| 5 | `src/apiforge/contracts/registry.py` | Modify | Register new `Name/v1` models for discovery and contract tooling | `@python-developer` | 1, 4 |
| 6 | `src/apiforge/runtime/evidence_gate.py` | Create | Evaluate required evidence, mode and unresolved gaps without side effects | `@data-quality-analyst` | 1–5 |
| 7 | `src/apiforge/runtime/promotion.py` | Create | Apply the promotion state machine and static fallback policy | `@genai-architect` | 1, 6 |
| 8 | `src/apiforge/evals/evidence_coverage.py` | Create | Compute explainable coverage over required and available evidence | `@data-quality-analyst` | 1–6 |
| 9 | `src/apiforge/runtime/routing.py` | Modify | Attach evolution mode/gate inputs while preserving deterministic eligibility and ranking | `@python-developer` | 1, 6, 7 |
| 10 | `src/apiforge/runtime/supervisor.py` | Modify | Call the gate before active execution and persist fallback/gaps | `@genai-architect` | 7, 9 |
| 11 | `src/apiforge/runtime/store.py` | Modify | Persist evolution decisions, coverage and gate receipts append-only | `@python-developer` | 1, 7, 10 |
| 12 | `src/apiforge/rules/agentic_runtime.yaml` | Modify | Configure Wave 0 modes and promotion policy without hardcoded runtime thresholds | `(general)` | 1, 7 |
| 13 | `docs/catalog-contract.md` | Modify | Catalog any new `AF-*` refusals and unlocks | `(general)` | 6, 7 |
| 14 | `docs/contracts/EvidenceCoverage-v1.md` | Create | Document the evidence coverage contract and limitations | `@data-quality-analyst` | 8 |
| 15 | `docs/contracts/RoutingEvolution-v1.md` | Create | Document mode/state transition and promotion semantics | `@genai-architect` | 1, 7 |
| 16 | `docs/contracts/PromotionGate-v1.md` | Create | Document gate inputs, refusals, fallback and receipts | `@genai-architect` | 6, 7 |
| 17 | `tests/contracts/test_routing_evolution.py` | Create | Contract validation, closed fields and illegal transitions | `@test-generator` | 1, 4, 5 |
| 18 | `tests/evals/test_evidence_coverage.py` | Create | Coverage, unknown, unresolved and partial evidence cases | `@test-generator` | 8 |
| 19 | `tests/runtime/test_evidence_gate.py` | Create | Gate decisions for each mode and missing evidence | `@test-generator` | 6 |
| 20 | `tests/runtime/test_promotion.py` | Create | Promotion, block and static fallback behavior | `@test-generator` | 7 |
| 21 | `tests/runtime/test_routing_modes.py` | Create | Supervisor/routing/store integration for local, replay, shadow and external-read | `@test-generator` | 9–11 |
| 22 | `tests/fixtures/agentic_runtime/evolution_cases.yaml` | Create | Golden, holdout and mutation-shaped fixtures for Wave 0 gate behavior | `@test-generator` | 17–21 |

**Total Files:** 22 Wave 0 entries

### Future sealed file groups (not part of this build)

| Wave | Candidate files | Required gate before opening |
|------|-----------------|-------------------------------|
| 1 | `src/apiforge/integrations/providers.py`, `src/apiforge/contracts/provider.py`, `tests/integrations/test_provider_adapters.py`, freshness fixtures | Wave 0 receipt and unresolved semantics are verified. |
| 2 | `src/apiforge/runtime/complexity.py`, `src/apiforge/runtime/adaptive_plan.py`, `src/apiforge/contracts/task.py`, adaptive-plan tests | Evidence Coverage explains plan inputs and static/adaptive replay is comparable. |
| 3 | `src/apiforge/runtime/optimizer.py`, `src/apiforge/evals/optimizer_gate.py`, optimizer fixtures/tests | Baseline, holdout, mutation and rollback artifacts are frozen. |
| 4 | `src/apiforge/cli_routing.py`, `src/apiforge/cli_knowledge.py`, `src/apiforge/cli.py`, `src/apiforge/cli_tui.py`, `src/apiforge/tui/app.py`, `src/apiforge/tui/fallback.py`, `src/apiforge/migration/matrix.py` | Shared contracts and projection parity are stable. |
| 5 | `src/apiforge/integrations/github.py`, `scripts/github_pr_host.py`, `.github/workflows/api-change-control.yml`, governance receipt docs/tests | External workflow, credential and policy are independently configured. |

---

## Agent Assignment Rationale

> Agents discovered from `${CLAUDE_PLUGIN_ROOT}/agents/` - Build phase invokes matched specialists.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| `@genai-architect` | 1, 7, 10, 15, 16 | Matches agentic routing, state-machine orchestration, guardrails and bounded promotion decisions. |
| `@data-quality-analyst` | 2, 3, 6, 8, 14 | Matches evidence coverage, data contracts, freshness and observability semantics. |
| `@python-developer` | 4, 5, 9, 11 | Matches existing Python runtime, Pydantic contracts, registries and clean layering. |
| `@test-generator` | 17–22 | Matches pytest fixtures, unit tests, integration tests and edge-case coverage. |
| `(general)` | 12, 13 | No exact plugin specialist owns API Forge YAML policy/catalog files; use project conventions and existing contracts. |

**Agent Discovery:**

- Scanned: `${CLAUDE_PLUGIN_ROOT}/agents/**/*.md`
- Matched by: file type, routing/evidence purpose, Python path, testing path and KB domains.
- Confidence: KB patterns and matching agents were found for architecture, Python, data quality and testing; external provider/GitHub work is intentionally deferred.

---

## Code Patterns

### Pattern 1: Closed immutable evolution contract

```python
from typing import Literal

from pydantic import model_validator

from apiforge.contracts.base import VersionedContract

EvolutionMode = Literal["local", "replay", "shadow", "external-read"]
PromotionState = Literal["planned", "observed", "simulated", "active", "blocked"]


class PromotionGate(VersionedContract):
    """Evidence-gated state for one routing evolution decision."""

    decision_id: str
    mode: EvolutionMode = "local"
    state: PromotionState = "planned"
    evidence_refs: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    fallback: str
    rollback_ref: str | None = None
    policy_version: str

    @model_validator(mode="after")
    def active_requires_proof(self) -> "PromotionGate":
        if self.state == "active" and (not self.evidence_refs or not self.rollback_ref):
            raise ValueError("active promotion requires evidence_refs and rollback_ref")
        return self
```

Use the existing `VersionedContract` rather than a free-form dictionary. New versions are sibling models; fields remain closed and immutable.

### Pattern 2: Pure gate with deterministic fallback

```python
from collections.abc import Iterable

from apiforge.contracts.base import ContractError
from apiforge.contracts.routing_evolution import PromotionGate


def evaluate_gate(
    *,
    decision_id: str,
    mode: str,
    required_evidence: Iterable[str],
    available_evidence: Iterable[str],
    fallback: str,
    policy_version: str,
    rollback_ref: str | None = None,
) -> PromotionGate:
    """Return a gate result without I/O or external authority."""
    required = set(required_evidence)
    available = set(available_evidence)
    missing = tuple(sorted(required - available))
    if mode not in {"local", "replay", "shadow", "external-read"}:
        raise ContractError(
            "AF-ROUTING-MODE",
            "field=mode; unlock=use an explicitly supported evolution mode",
        )
    if missing or mode in {"shadow", "external-read"}:
        return PromotionGate(
            decision_id=decision_id,
            mode=mode,  # type: ignore[arg-type]
            state="blocked" if missing else "observed",
            evidence_refs=tuple(sorted(available)),
            gaps=missing,
            fallback=fallback,
            rollback_ref=rollback_ref,
            policy_version=policy_version,
        )
    return PromotionGate(
        decision_id=decision_id,
        mode=mode,  # type: ignore[arg-type]
        state="simulated" if mode == "replay" else "active",
        evidence_refs=tuple(sorted(available)),
        fallback=fallback,
        rollback_ref=rollback_ref,
        policy_version=policy_version,
    )
```

The implementation must preserve the project convention that refusals expose an `AF-*` code, rejected field and safe unlock. Missing evidence is a result state, not an exception used to hide a gap.

### Pattern 3: Bounded adaptive plan as a proposal

```python
from collections.abc import Iterable

from apiforge.contracts.task import TaskPlan


def choose_plan(
    static_plan: TaskPlan,
    candidate_steps: Iterable[dict[str, object]],
    *,
    allowed_steps: frozenset[str],
    max_steps: int | None,
) -> tuple[TaskPlan, tuple[str, ...]]:
    """Return a candidate only when every deterministic bound is satisfied."""
    steps = tuple(candidate_steps)
    names = {str(step.get("name", "")) for step in steps}
    gaps: list[str] = []
    if not names.issubset(allowed_steps):
        gaps.append("candidate contains a step outside the allowlist")
    if max_steps is not None and len(steps) > max_steps:
        gaps.append("candidate exceeds the configured step budget")
    if gaps:
        return static_plan, tuple(gaps)
    return (
        TaskPlan(
            task_id=static_plan.task_id,
            revision=static_plan.revision,
            recipe=static_plan.recipe,
            steps=steps,
            proof_axes=static_plan.proof_axes,
        ),
        (),
    )
```

The first implementation should use this shape only for validation/replay. Execution remains bound to the existing `TaskSpec` budgets, dependencies and rollback.

### Pattern 4: YAML policy, not hardcoded tuning

```yaml
runtime:
  routing_evolution:
    active_wave: 0
    mode: local
    promotion: evidence_gated
    fallback: static-routing
    allow_external_mutation: false
    require_rollback_ref: true
    unknown_evidence: unresolved
    adaptive_plan:
      enabled: false
      max_steps: null
```

Unset thresholds resolve to `unresolved` or block promotion. The runtime must not invent provider limits, cost targets, freshness windows or learned weights.

---

## Data Flow

```text
1. Load TaskSpec, routing policy and evolution policy
   │
   ▼
2. Resolve local Knowledge Pack metadata and existing receipts
   │
   ▼
3. Build RoutingRequest and deterministic CandidateAssessment values
   │
   ▼
4. Calculate Evidence Coverage and collect explicit gaps
   │
   ▼
5. Wave 0: evaluate local/replay/shadow/external-read gate
   │       Future Wave 2: compile adaptive plan as a bounded candidate
   ▼
6. Select active route or static fallback; never widen allowlist or authority
   │
   ▼
7. Persist RoutingDecision, PromotionGate, coverage and trajectory events
   │
   ▼
8. Project the result to CLI/TUI/CI as observed, blocked, unresolved or active
```

### State transitions

```text
planned ──local evidence──> observed ──replay/eval──> simulated
   │                             │                       │
   └────missing/invalid──────────┴───────────────> blocked
                                                           │
                         rollback + evidence + policy ─────┘
                                                           ▼
                                                        active
```

`external-read` can produce `observed` but cannot independently grant `active`. `shadow` can produce `simulated` or `observed`, but learned weights remain non-authoritative until a later promotion gate.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| Local Knowledge Packs | Filesystem/YAML, deterministic loader | None; repository/workspace permissions only |
| Provider/model adapters (future Wave 1) | Injected read-only protocol and optional host execution | Host-injected credential; never imported into core |
| GitHub read-only adapter | GET-only HTTP transport and `af-change-bundle/1` replay | Injected host credential; receipt records limitations |
| GitHub mutation workflow (future Wave 5) | Dedicated CI job/host script | Explicit least-privilege token and repository policy |
| CLI/TUI | In-process projection of contracts and stored snapshots | Local filesystem; no extra authority |

No external integration is required to execute Wave 0. Provider and GitHub integrations remain future boundaries; their absence must be represented as `unresolved`, not simulated as success.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Evolution contracts, validators and illegal states | `tests/contracts/test_routing_evolution.py` | pytest + Pydantic validation | All contract fields, closed-model and transition rules |
| Unit | Evidence coverage and missing/unknown/unresolved semantics | `tests/evals/test_evidence_coverage.py` | pytest | All coverage classes and limitation paths |
| Unit | Gate decisions by mode and evidence set | `tests/runtime/test_evidence_gate.py` | pytest | All Wave 0 modes and refusal paths |
| Unit | Promotion and deterministic fallback | `tests/runtime/test_promotion.py` | pytest | Active, simulated, observed, blocked and rollback cases |
| Integration | Routing/supervisor/store persistence and replay | `tests/runtime/test_routing_modes.py` | pytest + local temporary workspace | Acceptance tests AT-001, AT-002, AT-007 |
| Fixture/evaluation | Golden, holdout and mutation-shaped routing states | `tests/fixtures/agentic_runtime/evolution_cases.yaml` | pytest fixture loader | No missing mandatory fixture class may be silently ignored |
| Existing regression | Prior routing, runtime gate, knowledge and GitHub boundaries | Existing `tests/runtime`, `tests/evals`, `tests/knowledge`, `tests/integrations` | pytest | No regression in shipped feature or read-only boundaries |
| Contract gate | DESIGN artifact conformance | `.claude/sdd/features/DESIGN_*.md` | AgentSpec spec-linter | PASS before build handoff |

The strategy covers all DEFINE acceptance tests: AT-001/002 through gate and freshness fixtures, AT-003 through the future plan seam and static fallback test, AT-004/008 through receipt/refusal contract tests in later waves, AT-005/006 through promotion and coverage tests, and AT-007 through shared projection tests when Wave 4 opens.

Independent verification must check the persisted artifacts rather than trusting only the returned in-memory result.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Invalid evolution contract or policy | Raise `ContractError` with cataloged `AF-*`, rejected field and unlock; do not persist a false success | No; repair the input/policy |
| Missing, stale or unresolved evidence | Return `blocked`/`observed` gate with gaps and static fallback; persist limitation | No core retry; collect a new receipt outside the core |
| Candidate adaptive plan violates allowlist/dependency/budget | Reject candidate, persist reason and use static plan | No automatic retry; revise candidate/policy |
| Provider or GitHub adapter timeout/failure | Preserve failure receipt/limitation and keep external state unresolved | Only a bounded retry at the explicit adapter/workflow boundary |
| Attempted external mutation from core/agent | Refuse with cataloged `AF-*`, `field` and `unlock`; do not call mutation transport | No; use the dedicated workflow |
| Corrupt persisted trace | Raise a named contract/runtime error and require replay or repair from the prior immutable artifact | No destructive repair |
| Test/evaluation gate missing mandatory evidence | Return `BLOCKED`, list missing case/kind and keep baseline | No promotion retry until evidence is added |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `runtime.routing_evolution.active_wave` | integer | `0` | Highest wave allowed in the current build; future waves remain disabled until their gate opens. |
| `runtime.routing_evolution.mode` | enum | `local` | Selects `local`, `replay`, `shadow` or `external-read`; unknown values are rejected. |
| `runtime.routing_evolution.promotion` | enum | `evidence_gated` | Selects the only Wave 0 promotion strategy. |
| `runtime.routing_evolution.fallback` | string | `static-routing` | Named deterministic fallback for missing or insufficient evidence. |
| `runtime.routing_evolution.allow_external_mutation` | boolean | `false` | Remains false in core; workflow policy owns any authorized mutation. |
| `runtime.routing_evolution.require_rollback_ref` | boolean | `true` | Prevents active promotion without a reversible artifact/reference. |
| `runtime.routing_evolution.unknown_evidence` | enum | `unresolved` | Maps missing evidence to an explicit unresolved state, never to pass. |
| `runtime.routing_evolution.adaptive_plan.enabled` | boolean | `false` | Reserved for Wave 2; false in Wave 0. |
| `runtime.routing_evolution.adaptive_plan.max_steps` | integer/null | `null` | Required before adaptive execution; null means candidate is not executable. |

No provider/model name, cost, latency, freshness window or learned weight is given an implicit runtime default.

---

## Security Considerations

- Keep `VersionedContract` models closed and immutable; reject unknown fields and invalid transitions.
- Treat freshness and capability as evidence attributes, not authority. A fresh receipt may still be incomplete or limited.
- Do not import provider SDKs, AWS clients or live database clients into `src/`; use injected adapters at explicit boundaries.
- Preserve prompt/tool guardrails: allowlists, risk acceptance, required evidence, budgets, timeouts and rollback remain enforced before execution.
- Keep all external mutations out of the core. The GitHub workflow/host is the only authorized mutation boundary and must emit its receipt.
- Redact secrets from receipts and projections; never persist credentials or raw authorization headers.
- Make refusal payloads actionable with cataloged `AF-*`, `field` and `unlock` values.
- Do not declare production support, deployment safety, authorship or permissions from local fixtures or model memory.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Append-only structured `TrajectoryEvent` entries with decision id, mode, policy version, gate state and unresolved gaps; avoid secrets and raw provider payloads. |
| Metrics | Persist deterministic counters/fields for gate state, evidence coverage components, fallback selection, adapter limitation and replay divergence; external dashboards are future projections. |
| Tracing | Extend `RunStore` routing traces with evolution mode, coverage, promotion gate, plan digest and receipt refs; replay strips non-deterministic event ids as the existing store does. |
| Receipts | Use versioned evidence/observation receipts with hashes, timestamps, freshness and limitations; receipts prove correspondence, not authorship. |
| Operator projection | CLI/TUI/CI show `active`, `simulated`, `observed`, `blocked` and `unresolved` distinctly; no collapsed boolean success. |

---

## Pipeline Architecture (if applicable)

> This is a local control-plane pipeline over decision artifacts, not an ETL deployment. The data-engineering patterns apply to lineage, freshness, idempotency and quality gates.

### DAG Diagram

```text
[TaskSpec + Policy]
        │
        ├──load──→ [Knowledge Pack Metadata / Receipts]
        │                    │
        ▼                    ▼
[Static Routing] ─────→ [Evidence Coverage]
        │                    │
        └──────────────→ [Promotion Gate]
                              │
              ┌───────────────┴────────────────┐
              ▼                                ▼
       [Active/Simulated]                [Fallback/Blocked]
              │                                │
              └───────────────┬────────────────┘
                              ▼
                  [RunStore / Replay / Brief]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|---------------|-------------|-----------|
| Run artifacts | `task_id/run_id` | One run directory | Isolates replay and prevents cross-run mutation. |
| Trajectory events | `run_id` plus append order | One event stream per run | Preserves causal order while keeping events append-only. |
| Knowledge/receipts | `domain/version/receipt_ref` | One immutable observation | Allows freshness verification without rewriting the pack. |
| Evaluation cases | `suite/case_id/kind` | One declared case | Keeps golden, holdout and mutation evidence distinguishable. |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Routing trace | Append-only event and immutable snapshot | `decision_id` | None; replay reads the recorded run |
| Evidence coverage | Recompute from referenced evidence and policy | `decision_id` + policy version | Explicit replay window only |
| Scorecard/optimizer candidates | Snapshot per evaluation run | `evaluation_id` | No implicit backfill; candidate must name baseline |
| Knowledge freshness | Read observation against pack metadata | `receipt_ref` + observed timestamp | Policy-defined; unknown blocks promotion |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| Add evidence field | Additive optional field or sibling versioned contract; update fixtures | Read previous contract version and use unresolved for missing field |
| Change promotion semantics | Create a new policy/contract version; never reinterpret historic active decisions | Pin the prior policy version for replay |
| Add adaptive-plan node | Validate against allowlist and preserve static `TaskPlan` fallback | Disable adaptive wave and replay static plan |
| Add provider capability | Add adapter receipt type with explicit limitations | Keep provider state `unresolved` and use local/fake adapter |
| Change GitHub workflow policy | Review external workflow and credential separately | Disable mutation job; core remains read-only |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Contract shape | Pydantic + spec-linter | No unknown fields or invalid required transitions | Block artifact/promotion and emit `AF-*` refusal |
| Evidence completeness | `evidence_coverage.py` + pytest | Policy-defined; missing required evidence is not pass | Keep `observed`/`blocked` and use fallback |
| Replay parity | `RunStore.replay` + golden fixtures | Same inputs/policy must produce equivalent deterministic decision | Block promotion and record divergence |
| Mutation boundary | Adapter/workflow tests | Core mutation count must remain zero | Refuse operation; require dedicated workflow |
| Freshness | Existing freshness verifier + receipts | Policy-defined; unknown/stale cannot silently promote | Keep limitation and request a new receipt |
| Holdout/mutation | Existing runtime gate plus future optimizer gate | All mandatory case kinds present before learning promotion | Keep baseline active and mark candidate blocked |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-24 | design-agent | Wave 0 evidence-gated architecture, future wave boundaries, file manifest and test strategy. |
| 1.1 | 2026-09-24 | build-agent | Wave 0 manifest completed with canonical contract exports/registry; implementation and verification complete. |
| 1.2 | 2026-09-24 | ship-agent | Shipped and archived. |

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md`
