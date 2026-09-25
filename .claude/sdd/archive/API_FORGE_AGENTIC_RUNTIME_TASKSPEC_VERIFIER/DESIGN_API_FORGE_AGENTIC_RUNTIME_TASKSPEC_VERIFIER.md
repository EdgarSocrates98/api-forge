# DESIGN: API Forge Agentic Runtime — TaskSpec e Verifier

> Technical design for implementing API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER |
| **Date** | 2026-09-22 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER.md](./DEFINE_API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
┌────────────────────────────────────────────────────────────────────────┐
│              API FORGE — VERIFIED AGENTIC VERTICAL SLICE               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  CLI / MCP                                                             │
│     │ same application-core services                                   │
│     ▼                                                                  │
│  Intent Compiler ──► TaskSpec v1 ──► Review ──► Ed25519 Seal           │
│                                      │                                 │
│                                      ▼                                 │
│                              Task Planner                              │
│                                      │ TaskPlan + closed steps         │
│                                      ▼                                 │
│                              Sandbox Executor                          │
│                           │           │           │                     │
│                           ▼           ▼           ▼                     │
│                       dispatch   read-only   evidence/artifacts         │
│                       allowlist  adapters     + run record             │
│                                      │                                 │
│                                      ▼                                 │
│                         Independent Verifier                           │
│                    ┌─────────┼──────────┬──────────┐                   │
│                    ▼         ▼          ▼          ▼                   │
│                contract   authZ     idempotency pagination              │
│                    └─────────┴──────────┴──────────┘                   │
│                                      │                                 │
│                                      ▼                                 │
│                           Holdout / Mutation Gate                      │
│                                      │                                 │
│                                      ▼                                 │
│                   Acceptance (distinct actor) → Outcome Brief          │
│                                                                        │
│  Persistent artifacts: .apiforge/tasks, case, sandbox, evidence        │
│  External AWS/databases: forbidden; only local fixtures/read-only       │
└────────────────────────────────────────────────────────────────────────┘
```

The runtime remains deterministic-core. An optional model or agent may propose an intent, but the application core only accepts validated contracts and registered verbs. The planner does not execute, the executor does not accept, and the verifier does not treat the executor's summary as proof.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Intent Compiler | Normalize a user/API intention plus local artifacts into a validated `TaskSpec` draft | Python, Pydantic v2, deterministic parsers |
| TaskSpec lifecycle | Review, revision, Ed25519 seal, state transitions and immutable history | Existing `contracts.task`, `taskspec.service`, JSON/YAML artifacts |
| Task Planner | Bind a sealed spec to a recipe and emit a closed `TaskPlan` with step preconditions and expected artifacts | Python, registered recipe data, dispatch metadata |
| Sandbox Executor | Execute only allowlisted verbs under budgets and writable-path gates | Existing `taskspec.runner`, `dispatch`, `sandbox`, `policy` |
| Read-only Adapter Layer | Resolve Commerce Orders PostgreSQL/Mongo/Redis dependencies from local doubles without mutation | Typed Python protocols and fixtures |
| VerificationRecord | Immutable result contract separating proof status from task/run status | New Pydantic contract, schema version 1 |
| Independent Verifier | Re-read sealed inputs and artifacts, rerun proofs, classify pass/fail/inconclusive and record gaps | New `verification` service; existing rules/evidence/sandbox APIs |
| Holdout/Mutation Gate | Apply known fixture mutation and require a failing proof | Local sandbox copy, deterministic mutation manifest |
| Acceptance/Brief integration | Require distinct acceptance and map verification-aware states to `OutcomeBrief` | Existing runner/brief extended with verification evidence |
| CLI surface | Expose compile/plan/verify/holdout without duplicating application logic | Typer wrappers in `cli.py` |
| MCP surface | Expose the same services with `detail_level` and economy accounting | Existing `mcp.tools` wrappers |

No new deployable service is introduced. All components run in the existing API Forge process and persist under the existing `.apiforge` structure.

---

## Key Decisions

### Decision 1: Extend the current TaskSpec family instead of creating a parallel runtime

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The repository already has versioned contracts, task revision/seal, recipes, a state machine, budgets, policy gates, sandbox isolation, receipts and distinct acceptance.

**Choice:** Keep `TaskSpec`, `TaskPlan`, `TaskHandoff` and `AcceptanceRecord` as the lifecycle backbone. Add only the missing compiler/planner/verifier contracts and services.

**Rationale:** This preserves CLI/MCP compatibility and makes the first slice incremental. The current `VersionedContract` uses closed Pydantic models and literal versions; new semantics can be added as sibling v1 contracts or compatible fields without silently changing old payloads.

**Alternatives Rejected:**
1. New Agent Runtime parallel — duplicates state, policy and evidence, creating divergence.
2. Event-sourcing first — useful later for replay, but not required to prove local/CI verification.

**Consequences:**
- Existing lifecycle and artifact conventions remain authoritative.
- The verifier must explicitly distinguish run records from proof records.
- A future event log can observe these records without being a prerequisite.

---

### Decision 2: Independent verification is a separate contract and service

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** A positive executor summary is not evidence that the intended behavior was proved. Reusing `AcceptanceRecord` would mix human acceptance with machine verification.

**Choice:** Introduce `VerificationRecord` with `task_id`, `revision`, `run_id`, `verdict`, `checks`, `evidence`, `gaps`, `limitations`, `holdout`, and `verified_by`. The service loads the sealed TaskSpec and artifacts independently and never receives the executor summary as an authority.

**Rationale:** The contract makes the separation testable and preserves the existing rule that `DONE` requires an independent acceptance. `pass`, `fail` and `inconclusive` are proof outcomes; `DONE`, `REVIEW` and `BLOCKED` remain brief/lifecycle outcomes.

**Alternatives Rejected:**
1. Boolean `verified=True` — loses evidence, limitations and unresolved state.
2. Extend `AcceptanceRecord` — conflates machine proof and human decision.

**Consequences:**
- Brief rendering must require a passing verification record for the new slice.
- Old tasks without a verification record retain their existing lifecycle semantics unless they opt into the new recipe.

---

### Decision 3: Planner emits a closed plan; executor rejects unbound steps

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Existing recipes are ordered data, but the new requirement needs every step to declare its input, path and expected proof before execution.

**Choice:** Add a planner that expands a recipe into immutable `TaskPlan.steps`. Each step contains `id`, `verb`, `inputs`, `writable_paths`, `expected_artifacts`, `proof_axes`, and `risk`. The executor validates the plan against the sealed revision before dispatch.

**Rationale:** This applies the `genai` plan-and-execute pattern without giving a model control over transitions. It also follows the project's protocol: routing and execution are data-driven, not inferred by an agent at runtime.

**Alternatives Rejected:**
1. Let the executor interpret the strategy dynamically — permits scope expansion.
2. Store only recipe name — insufficient for audit and per-step evidence.

**Consequences:**
- Recipe changes require plan regeneration and a new plan hash.
- An unknown verb or missing binding produces a named refusal before execution.

---

### Decision 4: Holdout/mutation is local, deterministic and evidence-bearing

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Green-path tests alone do not show that the proof detects regressions. The first slice cannot use external environments.

**Choice:** Store a mutation manifest in the Commerce Orders fixture. The holdout service applies one mutation at a time to a sandbox copy, runs the declared verifier checks, and records `mutation_id`, target hash, expected detection and observed result.

**Rationale:** It is reproducible offline and maps directly to the testing KB's mutation/negative-space guidance. A missed mutation downgrades the verification result and blocks `DONE`.

**Alternatives Rejected:**
1. Random mutation generation — nondeterministic and too broad for the first slice.
2. External fault injection — explicitly out of scope and unsafe without an environment gate.

**Consequences:**
- The fixture must contain at least auth/idempotency/cursor mutation definitions.
- Future language adapters can reuse the manifest protocol with language-specific mutators.

---

### Decision 5: CLI and MCP are thin projections over application services

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The project requires CLI/MCP parity and already records MCP economy/detail metadata.

**Choice:** Put compile, plan, verify and holdout logic in application/task services. CLI commands serialize service results; MCP wrappers call the same functions through `_call` and accept `detail_level`.

**Rationale:** This matches the existing MCP pattern and prevents two implementations of the lifecycle. The optional MCP extra remains optional for offline CI.

**Alternatives Rejected:**
1. Implement logic separately in `cli.py` and `mcp/tools.py` — guaranteed drift.
2. Make MCP mandatory — breaks the existing optional extra boundary.

**Consequences:**
- Parity tests compare normalized service outputs, not presentation formatting.
- CLI/MCP additions must not import model SDKs.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/task.py` | Modify | Add plan metadata/verification references only where backward-compatible | @api-planner | None |
| 2 | `src/apiforge/contracts/verification.py` | Create | `VerificationRecord`, `VerificationCheck`, `HoldoutRecord` closed contracts | @api-test-strategist | 1 |
| 3 | `src/apiforge/taskspec/compiler.py` | Create | Compile validated local intent/context into TaskSpec draft | @api-planner | 1, 2 |
| 4 | `src/apiforge/taskspec/planner.py` | Create | Expand sealed TaskSpec into hashed closed TaskPlan | @api-planner | 1, 2, 3 |
| 5 | `src/apiforge/taskspec/runner.py` | Modify | Validate/bind TaskPlan and persist run/verification references | @api-planner | 4, 6 |
| 6 | `src/apiforge/verification/__init__.py` | Create | Verification package boundary and public exports | @api-test-strategist | 2 |
| 7 | `src/apiforge/verification/service.py` | Create | Independent checks, evidence resolution and verdict aggregation | @api-test-strategist | 2, 4, 5, 8 |
| 8 | `src/apiforge/verification/holdout.py` | Create | Deterministic mutation manifest execution in sandbox | @api-test-strategist | 6, 9 |
| 9 | `src/apiforge/adapters/read_only.py` | Create | Protocols/doubles for PostgreSQL, Mongo and Redis read-only access | @api-data-access-architect | 2 |
| 10 | `src/apiforge/brief/render.py` | Modify | Require passing verification for the opted-in verified recipe | @api-release-guardian | 2, 7 |
| 11 | `src/apiforge/cli.py` | Modify | Add task compile/plan/verify/holdout commands as thin wrappers | @api-planner | 3, 4, 7, 8 |
| 12 | `src/apiforge/mcp/tools.py` | Modify | Add parity wrappers with `detail_level` and economy accounting | @api-release-guardian | 3, 4, 7, 8 |
| 13 | `src/apiforge/rules/recipes.yaml` | Modify | Add `verified-api-slice` recipe with closed ordered verbs | @api-planner | 4, 7, 8 |
| 14 | `tests/fixtures/orders_agentic/openapi.yaml` | Create | Commerce Orders contract with auth, idempotency and cursor requirements | @api-contract-architect | None |
| 15 | `tests/fixtures/orders_agentic/app.py` | Create | Minimal FastAPI implementation and intentional findings | @api-contract-architect | 14 |
| 16 | `tests/fixtures/orders_agentic/data.json` | Create | Deterministic orders/tenant data for read-only doubles | @api-data-access-architect | 15 |
| 17 | `tests/fixtures/orders_agentic/mutations.yaml` | Create | Auth, idempotency and cursor holdout definitions with target hashes | @api-test-strategist | 15 |
| 18 | `tests/agentic_runtime/conftest.py` | Create | Shared fixture roots, keypair, task and case builders | @api-test-strategist | 14–17 |
| 19 | `tests/agentic_runtime/test_compiler.py` | Create | Compiler contract, missing input and unresolved behavior | @api-test-strategist | 3, 14–17 |
| 20 | `tests/agentic_runtime/test_planner.py` | Create | Closed plan, step bindings, plan hash and seal mismatch | @api-test-strategist | 4, 18 |
| 21 | `tests/agentic_runtime/test_verifier.py` | Create | Independent checks, evidence, inconclusive and verdict mapping | @api-test-strategist | 7, 18 |
| 22 | `tests/agentic_runtime/test_holdout.py` | Create | Mutation detection and missed-mutation downgrade | @api-test-strategist | 8, 17, 18 |
| 23 | `tests/agentic_runtime/test_vertical_slice.py` | Create | Intent → TaskSpec → plan → sandbox → evidence → verify → accept → brief | @api-release-guardian | 19–22 |
| 24 | `tests/agentic_runtime/test_cli_mcp_parity.py` | Create | Normalize and compare application/CLI/MCP projections | @api-release-guardian | 11, 12, 23 |

**Total Files:** 24 (12 modify/create runtime files, 4 fixtures, 8 test files)

---

## Agent Assignment Rationale

> Agents discovered from `agents/**/*.md` and mirrored project agent directories. Matches use role, rule areas, executors and file purpose.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @api-planner | 1, 3, 4, 5, 11, 13 | Owns intent decomposition, sealed task planning, recipes and task CLI lifecycle |
| @api-test-strategist | 2, 6, 7, 8, 17–22 | Owns proof axes, contract tests, negative space, mutation and verifier evidence |
| @api-data-access-architect | 9, 16 | Owns data access boundaries and read-only database/cache abstractions |
| @api-contract-architect | 14, 15 | Owns API contract, operations, idempotency, pagination and Problem Details fixture |
| @api-release-guardian | 10, 12, 23, 24 | Owns independent acceptance, evidence gates, release semantics and parity |
| (general) | None | Every planned file has a domain-specialist match |

**Agent Discovery:**
- Scanned: `E:/projetos/api-forge/agents/**/*.md` and `.claude/agents/**/*.md`.
- Matched by: file purpose, rule area, lifecycle responsibility and existing executor boundaries.
- `af-verifier` remains the execution role inside the runtime; `api-test-strategist` owns proof design and `api-release-guardian` owns the terminal gate.

---

## Code Patterns

### Pattern 1: Closed verification contracts

```python
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract


class VerificationCheck(VersionedContract):
    check_id: str
    axis: Literal["contract", "security", "idempotency", "pagination"]
    verdict: Literal["pass", "fail", "inconclusive"]
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    limitation: str | None = None


class VerificationRecord(VersionedContract):
    task_id: str
    revision: int
    run_id: str
    verdict: Literal["pass", "fail", "inconclusive"]
    checks: tuple[VerificationCheck, ...] = ()
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    holdout_detected: bool = False
    verified_by: str

    def has_blocking_gap(self) -> bool:
        return bool(self.gaps) or self.verdict != "pass" or not self.holdout_detected
```

This follows the Python KB's typed/closed model pattern and the project convention that absence is represented explicitly, never silently defaulted to success.

### Pattern 2: Planner boundary and immutable plan

```python
from hashlib import sha256
import json

from apiforge.contracts.base import ContractError
from apiforge.contracts.task import TaskPlan, TaskSpec, TaskState


def plan_task(spec: TaskSpec, steps: tuple[dict[str, object], ...]) -> TaskPlan:
    if spec.state is not TaskState.SEALED:
        raise ContractError("AF-TASK-PLAN-UNSEALED", "plan requires a sealed revision")
    if not steps:
        raise ContractError("AF-TASK-PLAN-EMPTY", "a sealed task needs at least one step")
    for step in steps:
        if not step.get("verb") or not step.get("expected_artifacts"):
            raise ContractError("AF-TASK-PLAN-STEP", "every step needs verb and expected_artifacts")
    return TaskPlan(task_id=spec.id, revision=spec.revision, recipe=spec.strategy, steps=steps)


def plan_digest(plan: TaskPlan) -> str:
    payload = json.dumps(plan.model_dump(mode="json"), sort_keys=True)
    return sha256(payload.encode("utf-8")).hexdigest()
```

The executor must compare `plan.task_id` and `plan.revision` with the loaded sealed spec before dispatch. A plan is data; it does not execute itself.

### Pattern 3: Independent verifier aggregation

```python
def aggregate_checks(checks: tuple[VerificationCheck, ...]) -> str:
    if not checks:
        return "inconclusive"
    verdicts = {check.verdict for check in checks}
    if "fail" in verdicts:
        return "fail"
    if "inconclusive" in verdicts:
        return "inconclusive"
    return "pass"


def verify_task(task, plan, run_record, evidence) -> VerificationRecord:
    # Re-load task/plan/evidence from disk in the service; run_record is input,
    # not an authority. Every check returns evidence or an explicit gap.
    checks = tuple(
        run_check(axis, task, plan, evidence)
        for axis in ("contract", "security", "idempotency", "pagination")
    )
    return VerificationRecord(
        task_id=task.id,
        revision=task.revision,
        run_id=str(run_record["run_id"]),
        verdict=aggregate_checks(checks),
        checks=checks,
        evidence=tuple(sorted({item for c in checks for item in c.evidence})),
        gaps=tuple(sorted({item for c in checks for item in c.gaps})),
        holdout_detected=holdout_result.detected,
        verified_by="af-verifier",
    )
```

The real implementation must avoid accepting `run_record["summary"]` as proof; it is only an input pointer to artifacts.

### Pattern 4: Read-only adapter protocol

```python
from collections.abc import Mapping
from typing import Protocol


class ReadOnlyStore(Protocol):
    def get(self, key: str) -> Mapping[str, object] | None: ...
    def scan(self, prefix: str = "") -> tuple[Mapping[str, object], ...]: ...


class FixtureStore:
    def __init__(self, records: Mapping[str, Mapping[str, object]]) -> None:
        self._records = dict(records)

    def get(self, key: str) -> Mapping[str, object] | None:
        value = self._records.get(key)
        return dict(value) if value is not None else None

    def scan(self, prefix: str = "") -> tuple[Mapping[str, object], ...]:
        return tuple(dict(v) for k, v in sorted(self._records.items()) if k.startswith(prefix))
```

No `set`, `delete`, transaction or network method belongs in this first-slice protocol. Future Redis/Mongo/DynamoDB/Neptune adapters can implement the read-only contract behind explicit capability declarations.

### Pattern 5: Mutation manifest

```yaml
version: 1
mutations:
  - id: remove-auth-orders
    target: app.py
    operation: remove_security_requirement
    expected_detection: security
  - id: remove-idempotency-orders
    target: app.py
    operation: remove_idempotency_guard
    expected_detection: idempotency
  - id: accept-invalid-cursor
    target: app.py
    operation: bypass_cursor_validation
    expected_detection: pagination
```

Mutation operations are a closed allowlist interpreted by the local holdout service. The manifest is not executable shell text and cannot name an external command.

---

## Data Flow

```text
1. CLI/MCP receives intention + fixture paths + actor
   │
   ▼
2. Intent Compiler validates local inputs and writes TaskSpec draft
   │
   ▼
3. Existing review/seal lifecycle creates immutable revision + Ed25519 seal
   │
   ▼
4. Task Planner expands `verified-api-slice` into closed TaskPlan + digest
   │
   ▼
5. Runner validates revision/steps, applies policy, and executes in sandbox
   │
   ▼
6. Run record, facts, findings, artifacts and receipt are persisted
   │
   ▼
7. Independent Verifier reloads all inputs and runs four proof axes
   │
   ▼
8. Holdout service mutates one local copy and reruns the relevant proof
   │
   ▼
9. VerificationRecord is persisted; pass/fail/inconclusive is aggregated
   │
   ▼
10. Distinct actor accepts/rejects; brief derives DONE/REVIEW/BLOCKED
```

The only external-looking data path is the adapter interface; in this feature it resolves to fixture stores. Any missing input, unavailable tool or unsupported operation is a named gap/refusal, never a guessed success.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| CLI | Typer command wrappers | Local process identity; existing actor argument |
| MCP | Thin tool wrappers over application services | Optional MCP extra; no network required for core tests |
| OpenAPI | Local strict loader | None |
| FastAPI fixture | Static analyzer and sandbox copy | None; target code is not executed by extractors |
| PostgreSQL/Mongo/Redis | Local read-only test doubles | None |
| AWS/DynamoDB/Neptune | Not connected in this feature | Explicitly forbidden; future collector/adapter only |
| Ed25519 keys | Existing local key files | File permissions and existing key service |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Contracts, compiler, planner, digest, verdict aggregation, adapter refusal | `tests/agentic_runtime/test_compiler.py`, `test_planner.py`, `test_verifier.py` | pytest, Pydantic validation | 100% of new branches for refusal/pass/fail/inconclusive |
| Integration | Existing task store, seal, recipe, dispatch, sandbox, receipt and brief | `tests/agentic_runtime/test_vertical_slice.py` | pytest + local fixtures | Full AT-001–AT-012 path |
| Mutation/holdout | Auth/idempotency/cursor deliberate regressions | `tests/agentic_runtime/test_holdout.py` | pytest + sandbox copy | 100% of declared mutations detected |
| CLI/MCP parity | Same service inputs and normalized outputs | `test_cli_mcp_parity.py` | Typer runner; MCP tool functions when extra installed | All new public operations |
| Existing regression | Current TaskSpec, sandbox, evidence and MCP suites | Existing `tests/taskspec`, `tests/sandbox`, `tests/evidence`, `tests/mcp` | pytest, ruff, mypy | No regressions; release gate green |
| Offline CI | No network/credentials/external endpoints | `test_vertical_slice.py` | pytest with network-deny fixture if available | Deterministic repeated result |

Acceptance mapping:

- AT-001–AT-003 → compiler/planner unit tests.
- AT-004–AT-005 → sandbox and read-only adapter integration tests.
- AT-006–AT-007, AT-012 → verifier unit/integration tests.
- AT-008–AT-009 → holdout tests.
- AT-010–AT-011 → existing lifecycle/brief tests plus vertical slice.
- AT-013 → CLI/MCP parity tests.
- AT-014 → offline CI fixture and no-network assertion.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Intent input missing/unknown | Return `AF-TASK-INPUT` or `AF-TASK-CONTEXT` with field and unlock; persist unresolved diagnostic | No |
| Spec is not reviewed/sealed | Refuse compile/plan/execute with `AF-TASK-PLAN-UNSEALED` or existing transition code | No; review/seal required |
| Plan step lacks verb/input/proof | Refuse plan with `AF-TASK-PLAN-STEP`; no partial plan is executable | No |
| Plan revision/hash mismatch | Refuse execution with `AF-TASK-PLAN-STALE`; regenerate from current seal | No |
| Verb not registered or required input absent | Persist step as refused/pending with named missing field; task becomes parked/blocked per existing runner semantics | No automatic retry |
| Read-only adapter mutation attempt | Refuse with `AF-DATA-READONLY`; record target and unlock | No |
| Evidence missing or hash diverges | Verification check becomes `inconclusive`; receipt verifier identifies artifact mismatch | No; operator must regenerate evidence |
| Proof assertion fails | Check becomes `fail`; verifier continues independent checks to collect complete gaps | No blind retry |
| Holdout not detected | Verification becomes `inconclusive` or `fail` according to policy; `DONE` is prohibited | No |
| MCP extra unavailable | Return existing `AF-MCP-UNAVAILABLE`; CLI/application core remains usable | No |
| Deadline/budget exhausted | Existing runner records expired/blocked state and evidence of boundary | No; new reviewed task/run required |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `verified_recipe` | string | `verified-api-slice` | Recipe key used by the vertical slice |
| `required_proof_axes` | list[string] | `contract,security,idempotency,pagination` | Closed axes required for a passing verification |
| `holdout_manifest` | path | `mutations.yaml` | Fixture-relative mutation manifest |
| `max_holdout_mutations` | int | `3` | Maximum deterministic mutations per run; bounded by task budget |
| `allow_external_adapters` | bool | `false` | Hard-false for this feature; future features must add a policy gate |
| `verification_detail_level` | string | `normal` | `summary`, `normal` or `full` projection for CLI/MCP/economy |
| `offline_only` | bool | `true` | Refuse network-backed adapter resolution in the slice |

Tunables belong in recipe/fixture YAML or existing configuration, not in model prompts or scattered Python constants.

---

## Security Considerations

- Treat intent, fixture content, mutation manifests and run output as untrusted data; mutation operations are a closed enum, never shell text.
- Reuse existing path validation, policy decisions, sandbox copy and `writable_paths`; no verifier or holdout step may write outside `.apiforge`/the declared sandbox.
- Keep executor and acceptance identities separate; an executor cannot create the acceptance evidence that makes its own task `DONE`.
- Redact secrets and sensitive payloads from run records and MCP projections; `detail_level=summary` must not expose raw fixture bodies.
- Never load real AWS/database credentials; any future adapter must be an explicit capability outside this feature and must pass policy/identity gates.
- Evidence receipts prove byte correspondence, not authorship or freshness; the verifier must preserve that distinction.
- Unknown or dynamic routes, missing authorization facts and unsupported storage behavior remain `unresolved`/inconclusive rather than being treated as safe.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured JSON event entries in task history and run records: task/revision/plan digest/step/verdict/actor; no raw secrets |
| Metrics | Local counters in the run record: steps planned/executed/refused, proof axes pass/fail/inconclusive, mutations detected/missed, payload bytes by CLI/MCP detail level |
| Tracing | No external tracing dependency in the slice; correlate all artifacts with `task_id`, `revision`, `run_id`, `plan_digest`, `verification_id` and receipt hash |
| Evidence | Persist `TaskPlan`, run record, receipt, `VerificationRecord` and holdout records under deterministic task/case directories |
| Economy | MCP wrappers continue using `_call` and `detail_level`; no token saving claim is emitted without transcript/byte evidence |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | design-agent | Technical design from DEFINE; architecture, ADRs, manifest, patterns and testing strategy |
| 1.1 | 2026-09-22 | ship-agent | Shipped and archived |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER/`
