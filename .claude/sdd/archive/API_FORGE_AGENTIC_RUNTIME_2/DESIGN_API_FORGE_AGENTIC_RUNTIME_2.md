# DESIGN: API Forge Agentic Runtime 2.0

> Technical design for implementing API Forge Agentic Runtime 2.0

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_RUNTIME_2 |
| **Date** | 2026-09-22 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_AGENTIC_RUNTIME_2.md](./DEFINE_API_FORGE_AGENTIC_RUNTIME_2.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     API FORGE AGENTIC RUNTIME 2.0                  │
├─────────────────────────────────────────────────────────────────────┤
│ CLI / MCP / host adapter                                            │
│   │                                                                 │
│   ▼                                                                 │
│ Runtime Runner ──► Supervisor ──► TaskSpec Reviewer                 │
│   │                    │                                            │
│   │                    ├──► Planner / Capability Registry            │
│   │                    ├──► Dynamic Fan-out Scheduler                │
│   │                    ├──► Adversarial Critic                       │
│   │                    ├──► Debate Room / Referee                    │
│   │                    └──► Approval Gate                            │
│   │                                                                 │
│   ├──► Model Adapter (fake obrigatório; provider real opcional)     │
│   ├──► Tool/Policy Gateway (allowlist, sandbox, no external writes) │
│   ├──► Case/Task Store (events, artifacts, receipts, replay)        │
│   └──► Verifier / Holdout / Mutation / Outcome Brief                │
│                                                                     │
│ Canonical contracts: AgenticRun, Invocation, Artifact, Handoff,    │
│ Decision, ApprovalGate, TrajectoryEvent e AgenticPolicy              │
└─────────────────────────────────────────────────────────────────────┘

Flow:
intent → task review → sealed plan → fan-out → merge evidence
      → [critic/debate/approval when policy triggers]
      → sandbox execution → independent verification → final brief
```

The runtime is a local, persisted state machine. LLMs or external model
providers can propose structured outputs inside a node; only the runtime
controls transitions, policies, tools, evidence, budgets and terminal status.
The existing `TaskState` remains the lifecycle for a unit of work. The new
`AgenticRun` is the execution envelope bound to one sealed TaskSpec revision;
it does not replace TaskSpec, Debate or VerificationRecord.

**Design confidence:** 0.95. The design has both KB pattern and codebase
matches: the repository already contains TaskSpec transitions, append-only
task history, debate quorum/referee, dispatch allowlists, sandbox gates,
independent verification and outcome brief validation. The KB domains
`genai`, `testing`, `pydantic`, `python` and `terraform` were loaded; Terraform
is relevant only as a future read-only adapter and has no implementation impact
in this slice.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `AgenticRun` contracts | Closed, frozen, versioned schemas for run, invocation, artifact, handoff, decision, approval, policy and trajectory | Pydantic v2, `VersionedContract` |
| Runtime runner | Creates and resumes a run bound to `TaskSpec` revision; owns top-level lifecycle and terminalization | Python 3.12, synchronous CLI boundary + async internals |
| Supervisor | Classifies risk/complexity, selects capabilities, creates steps, triggers critic/debate/approval and routes transitions | Deterministic policy code; model only returns typed proposals |
| TaskSpec Reviewer | Validates scope, inputs, proof, rollback, dependencies, risk and writable paths before execution | Existing `TaskSpec` + new structured findings |
| Capability registry | Maps capabilities to agents, skills, tools, risk classes, output schemas and model preference | YAML data + profile metadata |
| Model adapter protocol | Provider-neutral request/response boundary with structured output and usage metadata | `Protocol`, async `invoke`, fake adapter |
| Dynamic scheduler | Runs independent invocations concurrently while enforcing budget, timeout, dependency and concurrency policy | `asyncio.TaskGroup`, semaphore, cancellation |
| Tool/policy gateway | Validates tool arguments and blocks paths, external mutations, unapproved operations and excessive agency | Existing dispatch/policy/sandbox boundaries |
| Evidence/artifact merger | Validates and stores typed outputs, deduplicates references and preserves unresolved claims | Pydantic validation, hashes, case files |
| Decision room | Converts evidence divergence or explicit user request into persisted debate, critic and referee flow | Existing `apiforge.debate` integration |
| Independent verifier bridge | Runs existing verification, holdout and mutation checks and binds result to run | Existing `apiforge.verification` |
| Trajectory/replay store | Append-only events and normalized replay view without timestamps or volatile IDs | JSONL + canonical JSON hashes |
| CLI/MCP surface | Starts, resumes, inspects and requests a debate room without exposing unsafe internals | Typer + existing MCP server |
| Agent profiles | Add orchestration, TaskSpec review and adversarial critic responsibilities | Markdown profiles under `agents/` |

### State model

```text
CREATED
  → TASK_REVIEWED
  → PLANNED
  → RUNNING
  → (DEBATING ↔ RUNNING)*
  → (AWAITING_SUPERVISION | VERIFYING | BLOCKED | FAILED)
  → COMPLETED
```

The runtime state is closed. A state transition requires a typed event and a
valid predecessor. `AWAITING_SUPERVISION` is entered for critical approval,
low confidence or unresolved debate. `COMPLETED` is not the user-facing
success claim; the final `OutcomeBrief` derives `DONE`, `REVIEW` or `BLOCKED`
from proof and gaps.

---

## Key Decisions

### Decision 1: Keep the API Forge state machine as the source of truth

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** A framework-first runtime could provide durable graphs, but the
project already owns TaskSpec, policy, evidence, debate, sandbox and verifier
contracts.

**Choice:** Implement a small runtime state machine over typed contracts and
reuse the existing TaskSpec lifecycle. Agents may reason inside a step; they
cannot choose arbitrary transitions.

**Rationale:** State-machine and agentic-workflow KB patterns require explicit
edges, fallbacks and human interrupts. Keeping those edges in API Forge avoids
provider lock-in and lets CLI, MCP, fake adapters and future model adapters
produce the same evidence.

**Alternatives Rejected:**
1. LangGraph as the core — introduces a runtime dependency and makes its state
   graph compete with TaskSpec and policy state.
2. Free-form agent loop — cannot provide reliable replay, bounded mutation or
   acceptance evidence.

**Consequences:**
- The project owns checkpoint and scheduling code.
- A future LangGraph adapter can map nodes to runtime phases without becoming
  authoritative.

### Decision 2: Versioned frozen contracts for every agentic artifact

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Raw model messages are not sufficient evidence and provider
schemas differ.

**Choice:** Add Pydantic v2 models extending `VersionedContract`, with
`extra="forbid"`, frozen instances, explicit statuses and references to facts,
artifacts and receipts.

**Rationale:** The existing contract registry, hash conventions and Pydantic
patterns already provide a stable compatibility boundary. Structured output is
validated with `model_validate_json()` before entering the run.

**Alternatives Rejected:**
1. Persist provider-native JSON — creates cross-model drift and unsafe fields.
2. Store only transcripts — loses typed provenance and makes verification
   dependent on language-model interpretation.

**Consequences:**
- New fields require a sibling contract version rather than silent mutation.
- Raw provider payloads may be retained as redacted evidence, but never as the
  canonical decision object.

### Decision 3: Fake adapter is mandatory; real provider is optional

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** CI must work without network, credentials or paid model calls.

**Choice:** Define an async `ModelAdapter` protocol and ship a deterministic
fake adapter driven by role/case fixtures. The runtime accepts a provider
adapter supplied by the host but does not package a provider SDK.

**Rationale:** This preserves local-first behavior and enables three-run replay
checks. It also satisfies the future Claude/GPT/Devin/Copilot compatibility
goal through a stable boundary.

**Alternatives Rejected:**
1. Multiple real providers in CI — nondeterministic, costly and network-bound.
2. Direct SDK imports — violates the deterministic-core boundary.

**Consequences:**
- Provider-specific tool calling, retries and token accounting belong in the
  adapter.
- The fake must model malformed outputs and failures, not only happy paths.

### Decision 4: Dynamic fan-out is policy-bounded

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Complexity varies by API change, but unrestricted parallelism can
  create cost explosions, races and unrepeatable decisions.

**Choice:** Supervisor emits a dependency DAG. Scheduler runs only ready nodes
  under `max_parallel_agents`, `max_calls`, `max_rounds`, deadline and risk
  policy. Default concurrency is 4; the value is configuration, not a hardcoded
  architectural limit.

**Rationale:** The concurrent and plan-and-execute patterns fit independent
  API review dimensions. The existing `Budgets` contract supplies a compatible
  call/round boundary.

**Alternatives Rejected:**
1. Strict sequential execution — safe but wastes independent specialist work.
2. Unlimited dynamic swarm — difficult to budget, cancel and replay.

**Consequences:**
- The scheduler must record admission, start, completion and cancellation.
- Results are merged in deterministic task/capability order, not completion
  order.

### Decision 5: Debate and adversarial criticism are triggered, not universal

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Debate improves difficult decisions but adds latency and tokens.

**Choice:** Open a Decision Room when a policy trigger detects high risk,
conflicting evidence, low confidence, close alternatives, unexplained
regression or explicit human request. High-risk changes always run the
adversarial critic before referee closure.

**Rationale:** Existing debate service already requires distinct sides,
`fact:*` evidence, quorum and referee. The runtime should supply triggers and
structured submissions instead of rewriting that protocol.

**Alternatives Rejected:**
1. Debate every task — unnecessary cost and noise.
2. Debate only when requested — misses safety-critical disagreements.

**Consequences:**
- Trigger decisions become part of the trajectory and are testable.
- An unresolved room blocks `DONE` and routes to supervision.

### Decision 6: External mutation remains outside the first runtime

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The first user-selected operating mode is local + CI without
external mutation.

**Choice:** Tool Gateway allows discovery, analysis, planning, sandbox and
verification only. AWS, database, observability-vendor and production actions
are recorded as `not_dispatchable` or `awaiting_supervision`.

**Rationale:** This reuses the existing dispatch allowlist, sandbox path checks,
approval and autonomy modes. It makes the first vertical slice safe to replay.

**Alternatives Rejected:**
1. Implicit credentials from the host — violates explicit scope and auditability.
2. Autonomous remediation — requires a later operational design with rollback,
   SLOs and incident controls.

**Consequences:**
- Future adapters can add capabilities without changing the core contracts.
- A provider tool call cannot bypass the gateway by returning shell text.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/agentic.py` | Create | AgenticRun, AgenticPolicy, AgentInvocation, AgentArtifact, HandoffRecord, DecisionRecord, ApprovalGate, TrajectoryEvent contracts | `@api-agentic-orchestrator` | `contracts/base.py`, `core/models.py` |
| 2 | `src/apiforge/contracts/registry.py` | Modify | Register all agentic contracts and expose schemas | `@api-agentic-orchestrator` | 1 |
| 3 | `docs/contracts/AgenticRuntime-v1.md` | Create | Document contract fields, invariants and status semantics | `@api-agentic-orchestrator` | 1 |
| 4 | `src/apiforge/runtime/__init__.py` | Create | Public runtime API and exports | `@api-agentic-orchestrator` | 1, 5 |
| 5 | `src/apiforge/runtime/adapters.py` | Create | ModelAdapter, request/response types, FakeModelAdapter and provider boundary | `@api-agentic-orchestrator` | 1 |
| 6 | `src/apiforge/runtime/policy.py` | Create | Risk triggers, budgets, tool gates, approval and debate policies | `@api-security-reviewer` | 1, existing `policy`/`autonomy` |
| 7 | `src/apiforge/runtime/registry.py` | Create | Capability/agent/tool registry loaded from YAML/profile metadata | `@api-planner` | 1, 6, 8 |
| 8 | `src/apiforge/rules/agentic_runtime.yaml` | Create | Declarative capabilities, role mapping, default limits and trigger rules | `@api-planner` | None |
| 9 | `src/apiforge/runtime/review.py` | Create | TaskSpec Reviewer and structured review findings | `@api-task-spec-reviewer` | 1, 6, existing `taskspec` |
| 10 | `src/apiforge/runtime/scheduler.py` | Create | Dependency-aware bounded dynamic fan-out with cancellation and receipts | `@api-agentic-orchestrator` | 1, 5, 6, 7 |
| 11 | `src/apiforge/runtime/rooms.py` | Create | Trigger evaluation and integration with debate/referee/critic flow | `@api-debate-referee` | 1, 6, 12, existing `debate` |
| 12 | `src/apiforge/runtime/critic.py` | Create | Adversarial review of plan and merged artifacts | `@api-adversarial-critic` | 1, 5, 6 |
| 13 | `src/apiforge/runtime/store.py` | Create | Append-only run events, artifacts, handoffs and normalized replay | `@api-agentic-orchestrator` | 1, existing `taskspec.store` |
| 14 | `src/apiforge/runtime/supervisor.py` | Create | Top-level deterministic supervisor and state transitions | `@api-agentic-orchestrator` | 5–13, existing `taskspec`, `verification`, `brief` |
| 15 | `src/apiforge/runtime/runner.py` | Create | Start/resume runtime, execute vertical slice and return brief | `@api-agentic-orchestrator` | 14 |
| 16 | `src/apiforge/taskspec/store.py` | Modify | Bind typed AgenticRun records to task run directory and preserve existing records | `@api-agentic-orchestrator` | 1, 13 |
| 17 | `src/apiforge/brief/render.py` | Modify | Render terminal run outcomes and keep `DONE` contract guard | `@api-release-guardian` | 1, existing `OutcomeBrief` |
| 18 | `src/apiforge/cli.py` | Modify | Add `runtime run`, `runtime status`, `runtime resume`, `runtime debate` and `runtime approve` | `@api-agentic-orchestrator` | 15 |
| 19 | `src/apiforge/mcp/tools.py` | Modify | Expose safe runtime start/status/resume/debate/approval tools | `@api-agentic-orchestrator` | 15, 18 |
| 20 | `docs/catalog-contract.md` | Modify | Document runtime commands, contracts, gates and AF error codes | `@api-dx-docs-reviewer` | 1, 18, 19 |
| 21 | `agents/api-agentic-orchestrator.md` | Create | Runtime supervisor role, handoffs, budgets and refusal boundaries | `@api-agentic-orchestrator` | 8 |
| 22 | `agents/api-task-spec-reviewer.md` | Create | Semantic TaskSpec review role and proof/rollback checks | `@api-task-spec-reviewer` | 9 |
| 23 | `agents/api-adversarial-critic.md` | Create | Independent attempt to disprove plans and evidence | `@api-adversarial-critic` | 12 |
| 24 | `agents/api-debate-referee.md` | Create | Evidence-bound debate closure and unresolved routing | `@api-debate-referee` | 11 |
| 25 | `tests/runtime/test_contracts.py` | Create | Contract validation, closed fields and registry conformance | `@api-test-strategist` | 1–3 |
| 26 | `tests/runtime/test_fake_adapter.py` | Create | Deterministic, malformed, timeout and provider-boundary adapter cases | `@api-test-strategist` | 5 |
| 27 | `tests/runtime/test_policy.py` | Create | Risk triggers, tool denial, approvals and budgets | `@api-security-reviewer` | 6 |
| 28 | `tests/runtime/test_scheduler.py` | Create | Dependency DAG, dynamic bounded parallelism and cancellation | `@api-test-strategist` | 10 |
| 29 | `tests/runtime/test_review.py` | Create | Valid/invalid TaskSpec review | `@api-task-spec-reviewer` | 9 |
| 30 | `tests/runtime/test_rooms.py` | Create | Automatic debate trigger, human room, quorum and referee | `@api-debate-referee` | 11, 12 |
| 31 | `tests/runtime/test_store_replay.py` | Create | Append-only events, normalized replay and receipts | `@api-test-strategist` | 13 |
| 32 | `tests/runtime/test_supervisor.py` | Create | State transitions, gates, critic ordering and failure paths | `@api-agentic-orchestrator` | 14 |
| 33 | `tests/runtime/test_security.py` | Create | Path escape, external mutation, tool allowlist and redaction refusal cases | `@api-security-reviewer` | 6, 10 |
| 34 | `tests/runtime/test_interfaces.py` | Create | CLI/MCP parity for runtime start, status, resume, debate and approval | `@api-dx-docs-reviewer` | 18, 19 |
| 35 | `tests/runtime/test_vertical_slice.py` | Create | End-to-end existing API evolution with fake adapter | `@api-test-strategist` | 15–19, 36 |
| 36 | `tests/fixtures/agentic_runtime/` | Create | Fake responses, divergent positions, invalid output and policy scenarios | `@api-test-strategist` | None |
| 37 | `tests/evals/test_runtime_evals.py` | Create | Structural evals for routing, evidence, refusal, critic and final status | `@api-evaluation-engineer` | 1, 14, 35 |
| 38 | `tests/evals/cases/runtime_cases.yaml` | Create | Declarative eval cases and expected outcomes | `@api-evaluation-engineer` | 37 |
| 39 | `evals/skills/evals.json` | Modify | Add runtime skill/eval entries without requiring real providers | `@api-evaluation-engineer` | 37, 38 |
| 40 | `scripts/check_release.py` | Modify | Validate agentic contracts, profiles, runtime rules and mirror/gate invariants | `@api-release-guardian` | 1, 8, 21–24 |

**Total Files:** 40 entries (new directories contain the listed fixture/eval files)

### Manifest implementation order

```text
1–3 contracts/docs
  ↓
5–8 adapters, policy, registry and config
  ↓
9–13 reviewer, scheduler, rooms, critic and store
  ↓
14–19 supervisor, runner and interfaces
  ↓
21–24 profiles
  ↓
25–38 tests, fixtures, evals, docs and release gate
```

No file may introduce a second persistence format for the same canonical
object. Runtime files use `.apiforge/tasks/<task_id>/runs/` for run-local
records and `.apiforge/tasks/<task_id>/history.jsonl` for lifecycle events;
artifacts referenced by the run store must carry content hashes.

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| `@api-agentic-orchestrator` | 1–5, 10, 13–16, 18–19, 21, 32 | Owns supervisor, runtime lifecycle, model boundary, scheduling and integration with TaskSpec. |
| `@api-task-spec-reviewer` | 9, 22, 29 | Owns semantic task review, proof, rollback, scope and preconditions. |
| `@api-adversarial-critic` | 12, 23 | Owns independent attempts to disprove high-risk plans and artifacts. |
| `@api-debate-referee` | 11, 24, 30 | Owns evidence-bound room lifecycle, quorum and unresolved decisions. |
| `@api-planner` | 7–8 | Owns capability routing, plan decomposition and declarative policy data. |
| `@api-security-reviewer` | 6, 27 | Owns tool gates, risk classification, excessive agency and approval boundaries. |
| `@api-release-guardian` | 17, 38 | Owns final brief integrity, release gate and no-false-DONE behavior. |
| `@api-test-strategist` | 25–26, 28, 31, 35–36 | Owns deterministic unit, integration and vertical-slice evidence. |
| `@api-evaluation-engineer` | 37–39 | Owns structural eval cases, routing accuracy and regression fixtures. |
| `@api-dx-docs-reviewer` | 20, 34 | Owns CLI/MCP and contract documentation parity. |

**Agent Discovery:**
- Scanned the repository `agents/**/*.md` catalog and existing profiles.
- Matched by runtime purpose, TaskSpec/debate/release specialization, testing
  responsibility and security boundary.
- Four profiles are new because orchestration, semantic TaskSpec review,
  adversarial criticism and referee are distinct responsibilities not covered
  by the existing 20 profiles.

---

## Code Patterns

### Pattern 1: Frozen versioned runtime contract

```python
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract


class AgenticRun(VersionedContract):
    run_id: str
    task_id: str
    revision: int
    state: Literal[
        "created",
        "task_reviewed",
        "planned",
        "running",
        "debating",
        "awaiting_supervision",
        "verifying",
        "completed",
        "blocked",
        "failed",
    ]
    policy_id: str
    invocation_ids: tuple[str, ...] = ()
    artifact_ids: tuple[str, ...] = ()
    decision_ids: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    final_status: Literal["DONE", "REVIEW", "BLOCKED"] | None = None
    started_at: str
    finished_at: str | None = None
    run_digest: str | None = None
```

Use `VersionedContract` for all persisted objects. Do not accept arbitrary
provider fields in the canonical contract. Provider payloads are normalized
before construction and rejected with `AF-RUNTIME-SCHEMA` when invalid.

### Pattern 2: Provider-neutral async adapter

```python
from collections.abc import Mapping
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    invocation_id: str
    agent: str
    capability: str
    prompt: str
    input_refs: tuple[str, ...] = ()
    tool_names: tuple[str, ...] = ()
    output_contract: str


class AgentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    output: Mapping[str, object]
    adapter: str
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    duration_ms: int | None = None
    tool_calls: tuple[str, ...] = ()


class ModelAdapter(Protocol):
    name: str

    async def invoke(self, request: AgentRequest) -> AgentResponse:
        ...
```

Every adapter must return structured output or a typed runtime error. The
runtime never parses free-form prose to infer a transition.

### Pattern 3: Policy-bounded fan-out

```python
import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")


async def run_bounded(
    items: list[T],
    worker: Callable[[T], Awaitable[object]],
    limit: int,
) -> list[object]:
    semaphore = asyncio.Semaphore(limit)

    async def invoke(item: T) -> object:
        async with semaphore:
            return await worker(item)

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(invoke(item)) for item in items]
    return [task.result() for task in tasks]
```

The scheduler must additionally check dependency readiness, deadline,
`max_calls`, cancellation and risk policy. Results are sorted by stable
invocation id before merge so completion order cannot change the decision.

### Pattern 4: Evidence-bound decision trigger

```python
def should_open_room(
    *,
    risk: str,
    confidence: float | None,
    unresolved: tuple[str, ...],
    conflicting_facts: bool,
    requested_by_user: bool,
) -> bool:
    return any(
        (
            requested_by_user,
            risk in {"sensitive", "external_mutation", "destructive", "irreversible"},
            conflicting_facts,
            bool(unresolved),
            confidence is not None and confidence < 0.70,
        )
    )
```

The trigger emits a `TrajectoryEvent`; it does not close the debate. Debate
closure remains subject to evidence, quorum and referee.

### Pattern 5: Declarative policy

```yaml
runtime:
  default_policy: local-ci-safe
  policies:
    local-ci-safe:
      max_parallel_agents: 4
      max_calls: 20
      max_rounds: 3
      timeout_seconds: 120
      allow_external_mutation: false
      require_critic_for_risk:
        - sensitive
        - external_mutation
        - destructive
        - irreversible
      require_human_gate_for:
        - external_mutation
        - destructive
        - irreversible
        - unresolved_debate
        - low_confidence
      debate_triggers:
        - conflicting_evidence
        - high_risk
        - low_confidence
        - user_requested
```

Policy is data, loaded and validated before a run. No provider response can
raise its own permissions or alter the policy.

---

## Data Flow

```text
1. CLI/MCP receives intention, case path, TaskSpec id and policy id.
   │
   ▼
2. Runner loads sealed TaskSpec revision and creates AgenticRun.
   │
   ▼
3. TaskSpec Reviewer checks scope, proof, rollback, dependencies, paths and risk.
   │
   ├── invalid → REVIEW/BLOCKED + findings + trajectory event
   │
   ▼
4. Supervisor resolves capabilities and creates a dependency-aware plan.
   │
   ▼
5. Scheduler fans out independent agent invocations through the adapter.
   │
   ▼
6. Responses are schema-validated, redacted, hashed and stored as artifacts.
   │
   ▼
7. Supervisor merges facts and detects risk, divergence, unresolved claims and gates.
   │
   ├── critic/debate/approval → room or supervision checkpoint
   │
   ▼
8. Allowed execution runs through existing sandbox/dispatch boundaries.
   │
   ▼
9. Independent verifier executes checks, holdout and mutation detection.
   │
   ▼
10. Runner persists receipt, normalized trajectory and OutcomeBrief.
```

Persistence layout:

```text
.apiforge/tasks/<task_id>/
  task.yaml
  revisions/<revision>.json
  history.jsonl
  runs/<index>.json
  runs/<index>/
    events.jsonl
    artifacts/<artifact_id>.json
    handoffs/<handoff_id>.json
    decisions/<decision_id>.json
    approvals/<gate_id>.json
    replay.json
    brief.json
```

The implementation may use an existing run JSON for backward compatibility,
but new runtime runs must reference a canonical `AgenticRun` and append events
atomically. A normalized replay excludes timestamps, volatile model IDs and
execution order while retaining stable inputs, policy, outputs, decisions and
verdicts.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| Existing TaskSpec service/store | In-process Python API | None; local case files |
| Existing debate service | In-process Python API | Actor/referee names recorded; no external identity claim |
| Existing verification/holdout | In-process Python API | Local sandbox and evidence paths |
| Existing dispatch/policy/sandbox | In-process gateway | Policy and recorded approval; no implicit credentials |
| CLI | Typer commands | Local filesystem/case path |
| MCP server | Tool wrappers | Host-controlled MCP session; mutating tools remain gated |
| Fake model adapter | In-process async adapter | None |
| Real model provider | Optional host-supplied adapter | Provider-specific credentials outside core; disabled in CI by default |
| Datadog/Dynatrace/OTel | Future adapter boundary only | Not implemented in this feature |
| AWS/databases/gRPC | Future adapter boundary only | Not implemented in this feature |

No network calls are made by the fake path. The runtime must not import
`openai`, `anthropic`, `litellm`, `boto3` or vendor SDKs in `src/apiforge/runtime`.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Pydantic contracts, hashes, policy trigger, error mapping | `tests/runtime/test_contracts.py`, `test_policy.py` | pytest, model validation | All branches of contract invariants and policy gates |
| Unit | Fake/real adapter boundary, malformed output, usage and failure classification | `tests/runtime/test_fake_adapter.py` | pytest, async fixtures | Happy path plus schema, timeout and provider errors |
| Unit | Scheduler DAG, bounded concurrency, deterministic merge and cancellation | `tests/runtime/test_scheduler.py` | pytest, `asyncio`, event probes | Dependency, budget, timeout and cancellation paths |
| Integration | TaskSpec review and existing stores | `tests/runtime/test_review.py`, `test_store_replay.py` | pytest, temporary case | No duplicate persistence and append-only replay |
| Integration | Debate room, quorum, critic ordering and approval gates | `tests/runtime/test_rooms.py`, `test_supervisor.py` | pytest, existing debate service | Every critical transition and refusal code |
| E2E | Existing API evolution vertical slice | `tests/runtime/test_vertical_slice.py` | pytest, local fixtures, fake adapter | AT-001, AT-003, AT-007–AT-010, AT-014 |
| Security | Path escape, external mutation, tool allowlist, output injection, secret redaction | `tests/runtime/test_policy.py`, `tests/runtime/test_security.py` | pytest, sandbox fixtures | Every unsafe tool attempt refused and evidenced |
| Evals | Routing, evidence grounding, refusal, critic and terminal status | `tests/evals/test_runtime_evals.py`, `runtime_cases.yaml` | pytest, deterministic scorer | 100% expected outcomes on fixture cases |
| Compatibility | CLI/MCP parity and contract registry | `tests/runtime/test_interfaces.py`, existing MCP tests | pytest, Typer runner | Same normalized result for CLI and MCP |
| Regression | Full existing suite, release gate, type/lint | repository test suite | pytest, ruff, mypy, `scripts/check_release.py` | Zero regression; all existing tests remain green |

Acceptance mapping:

| Acceptance IDs | Primary verification |
|----------------|----------------------|
| AT-001, AT-014 | `test_vertical_slice.py` |
| AT-002, AT-004, AT-011 | `test_review.py`, `test_fake_adapter.py`, `test_supervisor.py` |
| AT-003, AT-010 | `test_scheduler.py`, `test_store_replay.py` |
| AT-005, AT-006 | `test_rooms.py` |
| AT-007, AT-008 | `test_policy.py`, `test_supervisor.py` |
| AT-009 | Existing verification tests plus vertical slice |
| AT-012 | `test_security.py` |
| AT-013 | Adapter contract tests; real provider remains optional |

The fake adapter is the only mandatory E2E path. Real provider tests are
explicitly opt-in and must be marked `external`/`inconclusive` when the
provider is unavailable; they cannot make the local CI gate fail for missing
credentials.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Invalid TaskSpec | Refuse before run, persist reviewer findings and `REVIEW`/`BLOCKED` | No |
| Missing input/artifact | Persist missing reference and park/block the run | No, unless a new input is supplied |
| Adapter schema violation | Record `AF-RUNTIME-SCHEMA`, discard response as evidence | At most one bounded retry with same contract |
| Adapter timeout | Cancel invocation, persist timeout and budget usage | Bounded by policy; no infinite retry |
| Adapter transient failure | Persist provider error without exposing secrets | At most `max_retries` from policy |
| Tool not allowlisted | Refuse with `AF-RUNTIME-TOOL`, record attempted call | No |
| Path escape/external mutation | Refuse with `AF-RUNTIME-MUTATION`, preserve sandbox | No; requires gate/policy change |
| Budget exhausted | Stop new invocations and produce `REVIEW`/`BLOCKED` | No |
| Conflicting evidence | Open room if trigger applies; otherwise retain unresolved | No automatic resolution without evidence |
| Debate no quorum | Close `unresolved`, route to supervision | No |
| Critic failure on high risk | Block final decision; do not treat absence as pass | No |
| Verification inconclusive | Prevent `DONE`; produce `REVIEW` with gaps | No automatic acceptance |
| Store write failure | Fail closed; do not claim a terminal success without receipt | No |

Every error includes an `AF-*` code, field or artifact reference, unlock
condition and trajectory event. Raw provider exceptions are normalized and
redacted before persistence.

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `runtime.default_policy` | string | `local-ci-safe` | Named policy loaded from `agentic_runtime.yaml`. |
| `runtime.max_parallel_agents` | int | `4` | Default concurrent ready invocations; policy may lower or raise within host limits. |
| `runtime.max_calls` | int | `20` | Maximum model/tool calls for one run. |
| `runtime.max_rounds` | int | `3` | Maximum planner/review/retry rounds. |
| `runtime.timeout_seconds` | int | `120` | Default per-invocation/run deadline bound. |
| `runtime.max_retries` | int | `2` | Maximum bounded retry count for retryable adapter failures. |
| `runtime.allow_external_mutation` | bool | `false` | Must remain false in the first slice. |
| `runtime.critic_risks` | list[string] | sensitive, destructive, irreversible | Risk classes requiring adversarial critic. |
| `runtime.human_gate_reasons` | list[string] | external_mutation, unresolved_debate, low_confidence | Reasons that pause execution. |
| `runtime.debate_triggers` | list[string] | conflicting_evidence, high_risk, low_confidence, user_requested | Reasons to create a Decision Room. |
| `runtime.adapter` | string | `fake` | Adapter selection; real adapters are host-supplied and opt-in. |
| `runtime.replay_normalize` | bool | `true` | Strip volatile timestamps/order/model IDs from replay comparison. |
| `runtime.redact_sensitive` | bool | `true` | Redact secrets, auth headers, tokens and configured PII before storage. |

All tunables live in YAML and are validated into an immutable `AgenticPolicy`.
CLI flags can select a named policy but cannot silently expand permissions.

---

## Security Considerations

- Treat repository content, provider output and retrieved documents as
  untrusted data; never allow them to override runtime policy or system
  instructions.
- Validate every tool name and argument against an allowlist before execution.
  Path inputs must pass existing sandbox containment checks.
- Keep external mutation disabled in the default policy. A future enablement
  must require account, region, resource, impact, rollback and explicit
  approval evidence.
- Validate all provider outputs with Pydantic and reject extra fields; do not
  use prose or model confidence as authorization.
- Redact secrets, authorization headers, tokens, credentials, PII and raw
  sensitive payloads from prompts, artifacts, logs and replay bundles.
- Separate `executed_by` from `accepted_by`; a model or executor cannot accept
  its own work.
- Bind run records to TaskSpec revision and content hashes so a stale plan
  cannot execute against amended inputs.
- Preserve `unresolved`, `inconclusive`, `blocked` and `not_observed` instead
  of collapsing them into success.
- Cap calls, rounds, concurrency, output size and deadlines to prevent
  excessive agency and runaway cost.
- Treat adapter possession of credentials as an integration concern; the core
  never discovers or persists provider secrets.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured case events in `events.jsonl`, with run/task/revision/invocation/agent/capability IDs; redact before write. |
| Metrics | Local trajectory fields for call count, duration, token usage, retries, queue wait, concurrency peak, artifacts, evidence and final status. |
| Tracing | First slice records parent/child invocation relationships and normalized spans as trajectory events; OTel/Datadog/Dynatrace exporters are deferred. |
| Audit | Append-only task history, receipts, hashes, approvals, debate records and final brief. |
| Cost | Measured provider usage when available; fake/estimated values explicitly labeled `not_observed` or `estimated`. |
| Debugging | Replay bundle excludes volatile values and can reproduce fake adapter decisions from the same case, policy and contract inputs. |

No vendor backend is required for this feature. The event names and fields are
designed so a later OTel adapter can export agent, tool, debate and verifier
spans without changing the runtime contracts.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | design-agent | Initial technical design from DEFINE; architecture, contracts, manifest, patterns and tests. |
| 1.1 | 2026-09-22 | ship-agent | Shipped and archived. |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_AGENTIC_RUNTIME_2/`
