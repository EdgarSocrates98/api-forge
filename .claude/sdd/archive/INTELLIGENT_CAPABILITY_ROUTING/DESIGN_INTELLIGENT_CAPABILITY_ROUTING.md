# DESIGN: Intelligent Capability Routing

> Technical design for implementing Intelligent Capability Routing

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | INTELLIGENT_CAPABILITY_ROUTING |
| **Date** | 2026-09-24 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_INTELLIGENT_CAPABILITY_ROUTING.md](./DEFINE_INTELLIGENT_CAPABILITY_ROUTING.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

Framework confirmed: this feature is an internal Python 3.12 package using Pydantic contracts, YAML configuration and pytest; it does not introduce a web framework or provider SDK.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                 INTELLIGENT CAPABILITY ROUTING                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TaskSpec + evidence + AgenticPolicy                                   │
│                 │                                                       │
│                 ▼                                                       │
│       ┌─────────────────────┐                                          │
│       │ RoutingRequest       │  normalize declared inputs              │
│       └──────────┬──────────┘                                          │
│                  ▼                                                     │
│       ┌─────────────────────┐      Registry + Profiles + Policy        │
│       │ Eligibility filter  │◄───────────────────────────────────────┐ │
│       │ deterministic gate  │                                        │ │
│       └──────────┬──────────┘                                        │ │
│                  │ eligible candidates + rejection reasons            │ │
│                  ▼                                                     │ │
│       ┌─────────────────────┐      Scorecards + observed signals       │
│       │ Explainable ranker  │◄───────────────────────────────────────┐ │
│       │ stable tie-break    │                                        │ │
│       └──────────┬──────────┘                                        │ │
│                  ▼                                                     │ │
│       ┌─────────────────────┐                                          │ │
│       │ RoutingDecision      │──► RunStore/routing.json + events.jsonl │ │
│       └──────────┬──────────┘                                          │ │
│                  ▼                                                     │ │
│       ┌─────────────────────┐                                          │ │
│       │ Supervisor +         │──► bounded scheduler ──► fake adapter   │ │
│       │ invocation builder   │                                          │ │
│       └──────────┬──────────┘                                          │ │
│                  ▼                                                     │ │
│       ┌─────────────────────┐                                          │ │
│       │ Eval gate            │  golden + holdout + mutation             │ │
│       └──────────┬──────────┘                                          │ │
│                  ▼                                                     │ │
│       ┌─────────────────────┐                                          │ │
│       │ Scorecard feedback   │──► .apiforge/scorecards/*.json           │ │
│       │ evidence-gated       │                                          │ │
│       └─────────────────────┘                                          │ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

The architecture is a modular-monolith extension. Contracts are dependency-free domain inputs/outputs; runtime services consume them; storage and adapters remain at the boundary. The existing supervisor and scheduler remain the execution authorities. No external system is called by the MVP.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `RoutingRequest` / routing contracts | Normalize task requirements, evidence, policy and observations | Pydantic `VersionedContract` |
| Eligibility filter | Apply registry/profile state, accepted risks, prerequisites, evidence and policy before ranking | Pure Python functions |
| Explainable ranker | Order only eligible candidates by configured objective order and observed signals | Pure Python, stable sorting |
| `RoutingDecision` trace | Preserve candidates, rejections, signals, selected capability, fallback and unresolved gaps | Pydantic + JSON artifact |
| Routing policy loader | Read objective order, unknown-signal behavior and tie-break policy from the existing runtime YAML | PyYAML + validated contract |
| Runtime supervisor integration | Build invocations from the selected/fallback order and keep existing control/scheduler behavior | Existing async supervisor/scheduler |
| Scorecard feedback service | Convert persisted eval results and observations into a new scorecard record without silently promoting bad results | Python + existing scorecard store |
| RunStore projection | Persist `routing.json` and routing trajectory events alongside run/replay artifacts | Atomic JSON + JSONL |
| Evaluation gate | Require the existing golden, holdout and mutation categories before a scorecard update is considered quality evidence | Existing `run_runtime_gate` |
| YAML registry | Store tunable routing policy without hardcoding weights in Python | `src/apiforge/rules/agentic_runtime.yaml` |

Dependency direction:

```text
contracts
   ▲
   │
runtime/routing ──► runtime/registry ──► rules YAML
   │       │
   │       └────► capabilities/scorecard ──► evals/suite
   │
runtime/supervisor ──► runtime/scheduler
   │       │
   │       └────► runtime/store ──► TaskSpec store
   │
tests ──► all public boundaries
```

The contracts package never imports runtime services. The ranker never calls an adapter. The feedback service never authorizes execution.

---

## Key Decisions

### Decision 1: Two-phase eligibility then ranking

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** The current registry already combines eligibility and score ordering. The feature requires a stronger guarantee that historical quality, cost or latency cannot promote a candidate that fails risk, evidence or policy constraints.

**Choice:** Split the conceptual flow into a deterministic eligibility phase and an explainable ranking phase. Keep a compatibility wrapper for existing callers, but make the new routing service consume the separated results.

**Rationale:** This mirrors the `genai` KB state-machine principle that transitions are explicit and auditable, and the guardrail principle that pre-execution restrictions are applied before tool/agent execution. It makes the safety invariant locally testable: the ranker receives only eligible candidates.

**Alternatives Rejected:**
1. Ranking the complete registry - rejected because a high score must never bypass policy or evidence.
2. Replacing the registry with a new orchestrator - rejected because it would duplicate an existing authority and increase surface area.

**Consequences:**
- The candidate list contains both eligible candidates and explicit rejection reasons.
- Existing `select_eligible_capabilities` callers must retain deterministic behavior during migration.
- The ranker can be tested without model adapters, filesystem state or network access.

---

### Decision 2: Stable lexicographic ranking for the first slice

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** Efficiency is the primary user objective, while security must remain a near-equal guardrail and quality is a later preference. Exact numeric weights require an observed baseline that does not yet exist.

**Choice:** The first slice uses a configured objective order: safety remains a hard eligibility gate; among eligible candidates the ranker uses observed efficiency signals first, then verified quality, then a canonical capability identifier as the stable tie-break. Unknown signals are recorded as `unknown`/`unresolved` and never imputed.

**Rationale:** A lexicographic policy is deterministic and explainable while leaving the exact efficiency baseline and future weights for Design/Benchmark. It avoids false precision and keeps security as a non-compensable constraint. A later weighted or adaptive policy can consume the same `RoutingDecision` contract without changing execution authority.

**Alternatives Rejected:**
1. Hardcoded floating-point weights - rejected because the DEFINE leaves them unresolved and they would become unvalidated policy.
2. Online bandit/learned routing - rejected because the MVP lacks sufficient attributable history and needs stronger rollback/regression controls.

**Consequences:**
- The configuration expresses order and unknown-signal behavior, not provider-specific economics.
- Benchmark work can add weights later without changing eligibility or storage contracts.
- Two candidates with identical observed signals always resolve by the same canonical tie-break.

---

### Decision 3: Scorecard feedback is evidence-gated and append-oriented

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** `AgentScorecard` is currently derived from `EvalResult`, but the new loop must preserve gaps, evidence and non-pass verdicts rather than turning every execution into positive reputation.

**Choice:** The feedback service accepts only persisted eval results plus attributable observations. It writes a scorecard record with source cases, evidence, failed axes, last verdict and gaps. `PASS` can contribute to verified quality; `REVIEW` and `BLOCKED` remain visible and cannot be silently promoted as successful quality evidence.

**Rationale:** The evaluation-framework KB pattern separates evaluation samples/results from the policy gate, while the project already requires golden/holdout/mutation coverage. Keeping feedback behind the eval gate makes the routing loop auditable and replayable.

**Alternatives Rejected:**
1. Update scorecards after every adapter response - rejected because an unverified response is not a quality fact.
2. Discard `REVIEW`/`BLOCKED` results - rejected because gaps and negative evidence are operationally important.

**Consequences:**
- Scorecards may record new evidence without increasing pass reputation.
- The feedback service needs an explicit update decision in its artifact.
- Historical scorecards remain loadable; new dimensions are additive and optional until populated.

---

### Decision 4: Local-only execution boundary for the MVP

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** The project operating contract keeps model/provider integrations out of the core and requires external actions to be read-only and policy-gated.

**Choice:** Use the existing fake/local adapter path and local artifacts for the first closed loop. Do not add provider SDKs, network calls, external mutations or online optimizer behavior.

**Rationale:** This preserves deterministic replay and allows the feature to be verified in the repository without upgrading fixture evidence into production claims.

**Alternatives Rejected:**
1. Start with live provider observations - rejected because freshness, permission and authorship would remain unresolved.
2. Add a new database or telemetry service - rejected because the first slice needs no infrastructure and the existing append-only store is sufficient.

**Consequences:**
- Efficiency metrics are optional until a local observation is supplied.
- Provider integrations remain a separate design with receipts and policy gates.
- The implementation can run in CI/headless environments.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/routing.py` | Create | Versioned routing request, candidate assessment, observed signal, decision and feedback contracts | `@api-agentic-orchestrator` | None |
| 2 | `src/apiforge/contracts/agentic.py` | Modify | Add additive scorecard dimensions/observation references without breaking legacy fields | `@python-developer` | 1 |
| 3 | `src/apiforge/contracts/__init__.py` | Modify | Re-export public routing contracts if required by the package surface | `@python-developer` | 1 |
| 4 | `src/apiforge/runtime/routing.py` | Create | Load routing policy, normalize requests, filter eligibility and rank candidates | `@api-agentic-orchestrator` | 1, 2, 10 |
| 5 | `src/apiforge/runtime/feedback.py` | Create | Apply eval/evidence-gated scorecard feedback and preserve non-pass gaps | `@api-agentic-orchestrator` | 1, 2, 6, 9 |
| 6 | `src/apiforge/runtime/registry.py` | Modify | Preserve registry loading and expose eligibility without embedding the new ranking authority | `@api-agentic-orchestrator` | 1, 4 |
| 7 | `src/apiforge/runtime/supervisor.py` | Modify | Consume `RoutingDecision`, persist routing trace, build ranked invocations and invoke feedback boundary | `@api-agentic-orchestrator` | 4, 5, 8 |
| 8 | `src/apiforge/runtime/store.py` | Modify | Persist/load routing decision artifacts and routing trajectory events atomically | `@python-developer` | 1, 7 |
| 9 | `src/apiforge/capabilities/scorecard.py` | Modify | Derive additive dimensions and save feedback only with verified source references | `@python-developer` | 1, 2, 5 |
| 10 | `src/apiforge/rules/agentic_runtime.yaml` | Modify | Add versioned routing objective order, unknown-signal policy and tie-break configuration | `@api-agentic-orchestrator` | 4 |
| 11 | `tests/fixtures/agentic_runtime/routing_cases.yaml` | Create | Declarative cases for eligible/rejected candidates, unknown signals, ties and fallback | `@test-generator` | 1, 4, 10 |
| 12 | `tests/contracts/test_routing.py` | Create | Contract validation, frozen payloads, compatibility and actionable refusal fields | `@test-generator` | 1, 2 |
| 13 | `tests/runtime/test_routing.py` | Create | Pure eligibility/ranking tests, stable tie-breaks and deterministic replay | `@test-generator` | 4, 6, 10, 11 |
| 14 | `tests/runtime/test_feedback.py` | Create | Eval/evidence-gated scorecard updates and non-pass behavior | `@test-generator` | 5, 9, 11 |
| 15 | `tests/capabilities/test_scorecard.py` | Modify | Extend current persistence/order tests for multidimensional scorecards and gaps | `@test-generator` | 5, 9 |
| 16 | `tests/runtime/test_supervisor.py` | Modify | Integration proof that supervisor persists routing and preserves bounded execution | `@test-generator` | 7, 8, 13, 14 |
| 17 | `tests/evals/test_runtime_evals.py` | Modify | Ensure routing feedback cannot pass without golden/holdout/mutation evidence | `@data-quality-analyst` | 5, 9 |
| 18 | `docs/catalog-contract.md` | Modify if new refusal codes are needed | Catalog any new routing refusal; reuse existing codes first | `@code-reviewer` | 12 |

**Total Files:** 18 planned entries; the catalog entry is conditional and must not be changed unless the implementation introduces a new public refusal code.

---

## Agent Assignment Rationale

> Agents were discovered from the plugin agent tree and matched against project-local specialists. The local API Forge agent is preferred for runtime semantics; plugin agents provide general Python/testing/architecture coverage.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| `@api-agentic-orchestrator` | 1, 4, 5, 6, 7, 10 | Project-local specialist matches supervisor, capability routing, bounded execution and agentic runtime policy |
| `@python-developer` | 2, 3, 8, 9 | Plugin specialist matches typed Python, Pydantic contracts, clean layering and artifact persistence |
| `@test-generator` | 11, 12, 13, 14, 15, 16 | Plugin specialist matches pytest fixtures, unit tests, integration tests and edge-case coverage |
| `@data-quality-analyst` | 17 | Plugin specialist matches quality dimensions, eval evidence and gate semantics |
| `@code-reviewer` | 18 and cross-cutting review | Plugin specialist matches security, error handling, maintainability and refusal catalog review |
| `@genai-architect` | Design reference, no direct file ownership | Plugin agent matches the `genai` KB; its supervisor/state-machine patterns support the architecture rationale |

**Agent Discovery:**

- Scanned: `C:\Users\edgar\.codex\plugins\cache\agentspec\agentspec\3.6.0\agents/**/*.md` and project-local `.claude/agents/`/`agents/`.
- Matched by: file type, runtime/capability purpose, Python/Pydantic/testing KB domains and project-local API Forge ownership.
- Confidence: **0.95**, because the relevant KB patterns and direct project agents both match the proposed files.

---

## Code Patterns

### Pattern 1: Separate eligibility from ranking

```python
from collections.abc import Mapping, Sequence

from apiforge.contracts.routing import CandidateAssessment, RoutingRequest
from apiforge.runtime.registry import Capability


def assess_candidates(
    capabilities: Mapping[str, Capability],
    profiles: Mapping[str, object],
    request: RoutingRequest,
) -> tuple[CandidateAssessment, ...]:
    """Return auditable assessments before any ranking is attempted."""
    assessments: list[CandidateAssessment] = []
    for capability in sorted(capabilities.values(), key=lambda item: item.name):
        rejection = check_eligibility(capability, profiles, request)
        assessments.append(
            CandidateAssessment(
                capability=capability.name,
                agent=capability.agent,
                eligible=rejection is None,
                rejection=rejection,
            )
        )
    return tuple(assessments)


def rank_eligible(
    assessments: Sequence[CandidateAssessment],
    *,
    scorecards: Mapping[str, object],
    policy: RoutingPolicy,
) -> tuple[CandidateAssessment, ...]:
    """Rank only eligible candidates with a deterministic final tie-break."""
    eligible = [item for item in assessments if item.eligible]
    return tuple(
        sorted(
            eligible,
            key=lambda item: ranking_key(item, scorecards, policy),
        )
    )
```

The implementation must keep `check_eligibility` free of scorecard ordering. Rejection data carries the refusal code, field, unlock and evidence gap required by the public contract.

### Pattern 2: Versioned Pydantic boundary with explicit unknowns

```python
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract


class ObservedSignal(VersionedContract):
    name: Literal["cost", "duration", "quality", "security"]
    value: float | None = Field(default=None, ge=0)
    status: Literal["observed", "unknown", "unresolved"] = "unknown"
    evidence_refs: tuple[str, ...] = ()


class CandidateAssessment(VersionedContract):
    capability: str
    agent: str
    eligible: bool
    rejection: dict[str, str] | None = None
    signals: tuple[ObservedSignal, ...] = ()
    ranking_key: tuple[str, ...] = ()


class RoutingDecision(VersionedContract):
    decision_id: str
    task_id: str
    policy_id: str
    candidates: tuple[CandidateAssessment, ...]
    selected: str | None = None
    fallback_order: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
```

`None` and `unknown` are not converted to a score. `ranking_key` is persisted so a replay can explain and compare the exact ordering.

### Pattern 3: Evidence-gated feedback

```python
def update_scorecard(
    profile: AgentCapabilityProfile,
    results: tuple[EvalResult, ...],
    *,
    observations: tuple[ObservedSignal, ...],
    gate: Mapping[str, object],
) -> AgentScorecard:
    """Record eval outcomes; only verified results may improve reputation."""
    if gate.get("status") != "PASS":
        return build_scorecard(
            profile,
            results,
            observations=observations,
            allow_quality_promotion=False,
        )
    if not results or any(not result.evidence for result in results):
        raise ContractError("AF-RUNTIME-EVAL-GATE", "scorecard feedback lacks eval evidence")
    return build_scorecard(profile, results, observations=observations)
```

The exact implementation may use a dedicated feedback contract, but the service must keep gate evaluation separate from scorecard persistence and preserve failed axes/gaps.

### Pattern 4: Declarative routing configuration

```yaml
runtime:
  routing:
    policy_version: "routing/v1"
    objective_order: [efficiency, quality]
    security_mode: gate
    unknown_signal: unresolved
    tie_breaker: capability
    scorecard_update: eval_required
```

Security is a gate in the first policy, not a compensable weighted preference. Numeric weights remain a benchmark-backed extension and must not be hardcoded in Python.

---

## Data Flow

```text
1. Supervisor loads TaskSpec, policy, registry, profiles, scorecards and available evidence.
   │
   ▼
2. RoutingRequest normalizes requested capabilities, risk, prerequisites, evidence and budget.
   │
   ▼
3. Eligibility filter evaluates every declared candidate and records eligible/rejected reasons.
   │
   ▼
4. Ranker consumes eligible candidates only, reads observed signals, builds stable ranking keys and chooses a fallback order.
   │
   ▼
5. RunStore persists RoutingDecision; supervisor creates invocations in that order and scheduler enforces timeout/retry/call limits.
   │
   ▼
6. Adapter results become artifacts and trajectory events through existing supervisor/store boundaries.
   │
   ▼
7. Verification/eval runs the declared golden, holdout and mutation cases.
   │
   ▼
8. Feedback service records the eval-linked scorecard update, preserving gaps and non-pass verdicts.
   │
   ▼
9. Later routing loads the scorecard and uses it only to order candidates that pass eligibility.
```

Persistence is append-oriented for decisions and events. Existing atomic `RunStore._write` remains the write primitive. Scorecard files continue to live under `.apiforge/scorecards/`; a future migration must be additive and digest old/new representations.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| TaskSpec store | Internal local file store | None |
| Capability/profile YAML | Internal read-only configuration | None |
| `ControlPlane` and scheduler | In-process application boundary | Policy object |
| Fake model adapter | In-process test adapter | None |
| Eval cases and runtime gate | Internal local files/functions | None |
| Scorecard store | Local JSON artifacts | None |
| External model/provider | Not used in MVP | N/A; future adapter requires explicit policy/receipt |

No network, database, AWS, GitHub or provider mutation is introduced by this design.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Contract unit | Pydantic validation, unknown signals, refusal fields and legacy compatibility | `tests/contracts/test_routing.py` | pytest | Every routing contract branch and invalid payload |
| Eligibility unit | State, enabled flag, risk, prerequisites and evidence filter | `tests/runtime/test_routing.py` | pytest + parametrization | Every rejection reason and zero-eligible path |
| Ranking unit | Objective order, observed/unknown signals, stable tie-break and replay | `tests/runtime/test_routing.py` | pytest | Every configured ranking branch |
| Feedback unit | PASS/REVIEW/BLOCKED, missing evidence, gaps, source refs and scorecard digest | `tests/runtime/test_feedback.py`, `tests/capabilities/test_scorecard.py` | pytest + fixtures | No silent score promotion and all update outcomes |
| Store integration | Routing JSON, trajectory event, atomic rewrite and replay normalization | `tests/runtime/test_supervisor.py` | pytest + `tmp_path` | Persisted trace matches decision contract |
| Supervisor integration | Route → bounded execution → artifact → eval boundary | `tests/runtime/test_supervisor.py` | pytest + fake adapter | All DEFINE acceptance paths through the runtime |
| Eval regression | Golden/holdout/mutation completeness and blocked gate | `tests/evals/test_runtime_evals.py` | pytest + YAML fixtures | Gate refuses incomplete quality evidence |
| Mutation/holdout | Change ranking inputs, scorecards and evidence to detect unsafe promotion | `tests/fixtures/agentic_runtime/routing_cases.yaml` + eval corpus | Existing eval gate | Zero tolerated unsafe selection; unresolved states stay visible |
| Static quality | Types, lint and SDD contract | source tree and design artifact | `ruff`, `mypy`, spec-linter, `apiforge sdd check` | Existing project gates remain green |

The acceptance tests from DEFINE map as follows: AT-001–AT-006 to routing/contract units; AT-007–AT-008 to feedback units; AT-009–AT-010 to replay/supervisor integration; AT-011–AT-012 to eligibility/eval regression; AT-013 to contract compatibility.

No external integration test is planned for the MVP because external systems are explicitly out of scope.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Invalid registry/profile YAML | Raise existing `AF-RUNTIME-REGISTRY`/`AF-RUNTIME-PROFILES`; include rejected field and unlock at the public boundary | No; fix configuration |
| Invalid routing policy | Raise `AF-RUNTIME-POLICY`; preserve source/path context and instruct operator to correct the policy | No |
| Invalid scorecard JSON/schema | Raise `AF-SCORECARD-INVALID`; ignore no bytes silently and use an explicit no-history fallback only when policy allows | No automatic mutation; operator repair |
| No eligible capability | Return `AF-CAPABILITY-ELIGIBILITY` with `field`, `unlock` and `unresolved` gap | No; correct inputs or policy |
| Unknown cost/duration/quality signal | Keep signal `unknown`/`unresolved`, omit it from the ranking component and record the limitation | No |
| Scheduler timeout/retry/call budget | Preserve existing `AF-RUNTIME-BUDGET` and scheduler status; follow configured bounded retry behavior | Yes only within policy budget |
| Missing golden/holdout/mutation evidence | Return `AF-RUNTIME-EVAL-GATE`; do not promote feedback as quality evidence | No |
| Scorecard feedback persistence error | Fail the feedback step, preserve the run result and unresolved gap; do not claim update success | No automatic overwrite |
| Legacy scorecard without new fields | Load additive defaults and mark missing dimensions unknown | No |

All public refusals must preserve the project contract: `AF-*` code, rejected `field`, actionable `unlock`, evidence/gaps and unresolved state. A new public code requires a catalog update in `docs/catalog-contract.md` and its own test.

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `runtime.routing.policy_version` | string | `routing/v1` | Version of the ranking/trace contract |
| `runtime.routing.objective_order` | list[string] | `[efficiency, quality]` | Ordered objectives after hard eligibility gates |
| `runtime.routing.security_mode` | string | `gate` | Keeps security/risk as a non-compensable eligibility constraint |
| `runtime.routing.unknown_signal` | string | `unresolved` | Behavior for missing observations; never converts to zero |
| `runtime.routing.tie_breaker` | string | `capability` | Stable canonical ordering for identical keys |
| `runtime.routing.scorecard_update` | string | `eval_required` | Requires persisted eval/evidence before quality promotion |
| `runtime.routing.allow_adaptive_optimizer` | bool | `false` | Reserved; must remain false in the MVP |

Configuration is loaded from the existing `agentic_runtime.yaml` and validated before a run starts. Numeric weights, if introduced later, must be added as versioned policy fields with benchmark evidence.

---

## Security Considerations

- Treat registry YAML, profiles, scorecards and observed signals as untrusted input at the contract boundary; validate with Pydantic and preserve source/digest references.
- Apply risk, policy, prerequisites and evidence gates before ranking; no historical score can grant a forbidden capability.
- Do not import `openai`, `anthropic`, `litellm` or other model SDKs into the core; the MVP remains fake/local and offline-first.
- Do not infer provider permission, cost, freshness, production support or safety from a fixture. Unknown observations remain `unknown`/`unresolved`.
- Redact sensitive values in routing traces according to the existing `AgenticPolicy.redact_sensitive` behavior; persist references and hashes rather than secrets.
- Ensure every refusal remains actionable with `AF-*`, `field`, `unlock` and evidence limitations.
- Preserve append-oriented run artifacts and stable digests so a later scorecard cannot rewrite the historical reason for a decision.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Existing structured `TrajectoryEvent` records for `routing_assessed`, `routing_ranked`, `routing_selected`, `routing_fallback` and `scorecard_feedback`; no sensitive payloads |
| Metrics | Persist observed `duration_ms`, token counts and optional cost signal in routing/scorecard artifacts; unknown metrics remain unresolved and are not emitted as zero |
| Tracing | `routing.json` stores the versioned decision, ranking keys, candidates, rejections, evidence refs, scorecard digests and unresolved gaps; `RunStore.replay()` includes normalized routing events |
| Correlation | Use existing `run_id`, `task_id`, `invocation_id`, `decision_id`, `profile_id` and artifact digests |
| Review surface | Existing JSON/CLI runtime projections can expose the persisted trace later; no new TUI is required for this slice |

The trace is the authoritative local projection of why a choice was made. It proves correspondence to local artifacts, not authorship or production performance.

---

## Pipeline Architecture (if applicable)

Not applicable. This feature is a local runtime decision/evaluation loop, not an ETL, warehouse or streaming pipeline. Its artifact flow is documented in **Data Flow** and its contract lineage in **Integration Points**, **Security Considerations** and **Observability**.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-24 | design-agent | Initial architecture from validated DEFINE; KB confidence 0.95 |
| 1.1 | 2026-09-24 | ship-agent | Shipped and archived |

---

## Next Step

**Archived:** `.claude/sdd/archive/INTELLIGENT_CAPABILITY_ROUTING/`
