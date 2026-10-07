# DESIGN: API Forge Agentic Kernel Evolution

> Desenho técnico para integrar o runtime agêntico determinístico, provas de qualidade, self-healing seguro e uma projeção DX canônica.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_KERNEL_EVOLUTION |
| **Date** | 2026-09-23 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_AGENTIC_KERNEL_EVOLUTION.md](./DEFINE_API_FORGE_AGENTIC_KERNEL_EVOLUTION.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                  API FORGE AGENTIC KERNEL — LOCAL CONTROL PLANE             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  CLI / MCP / IDE / UI projections                                         │
│             │                                                              │
│             ▼                                                              │
│  RuntimeExperience facade ──► TaskSpec + Policy + Capability Registry      │
│             │                         │                                    │
│             └───────────────► Supervisor / Planner / Review                │
│                                           │                                │
│                                           ▼                                │
│  ┌────────────────────── ControlPlane (authority) ──────────────────────┐  │
│  │ DAG readiness │ lease/heartbeat │ retry/budget │ checkpoint │ cancel  │  │
│  │ idempotency   │ state transition │ event journal │ replay              │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
│                                 │ ready steps                              │
│                                 ▼                                           │
│  Bounded Scheduler ──► Model/Tool adapters ──► typed AgentArtifact         │
│         │                         │                    │                   │
│         │                         └──── no external mutation by default    │
│         ▼                                              ▼                   │
│  persisted RunStore / TaskStore ───────────────► Evidence + Eval Gate      │
│         │                                              │                   │
│         ▼                                              ▼                   │
│  AgenticRun projection ◄──────── independent verifier / critic / referee    │
│         │                                                                  │
│         ▼                                                                  │
│  Outcome Brief: DONE only with proof; otherwise REVIEW / BLOCKED / gaps    │
│                                                                            │
│  Self-healing lane: snapshot → execute → verify → CAS compare              │
│                              └─ mismatch → conflict, never overwrite       │
└────────────────────────────────────────────────────────────────────────────┘
```

The `ControlPlane` in `src/apiforge/runtime/control.py` is the lifecycle
authority. The existing `AgenticRun` remains the provider-neutral projection
used by TaskSpec, briefs and existing consumers. The supervisor must persist
both views through one transition path; neither the scheduler nor a CLI
command may invent a second lifecycle state machine.

The implementation is delivered in four slices, each ending in a DX projection
and a quality gate:

1. **Kernel safety:** DAG execution, leases, checkpoints, retry/budget,
   cancellation, resume, idempotency and replay.
2. **Safe recovery:** compare-and-swap rollback and explicit conflict evidence.
3. **Capability quality:** profile-based routing, scorecards and mandatory
   golden/holdout/mutation runtime evaluations.
4. **Canonical DX:** `doctor`, `status`, `review`, `evolve` and `resume` call
   application services and project the same contracts as expert commands.

No slice adds provider SDKs, network mutation or a production claim.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Versioned runtime contracts | Carry lifecycle, invocation, profile, scorecard, checkpoint and evidence references without silently changing old payloads | Pydantic `VersionedContract`, frozen/closed models |
| ControlPlane | Own the persisted run/step state machine, DAG readiness, leases, retry, budget, cancel, idempotency and replay | JSON + JSONL under `.apiforge/control` |
| Bounded Scheduler | Execute only ControlPlane-ready work within policy limits and deterministic ordering | `asyncio`, `wait_for`, bounded fan-out |
| Supervisor | Review TaskSpec, create the plan, select eligible capabilities, invoke workers and request independent verification | Existing provider-neutral runtime supervisor |
| RunStore and TaskStore | Persist immutable artifacts, event projections, hashes and backward-compatible run indexes | Local filesystem, content hashes |
| Self-healing CAS lane | Restore only when the current bytes match the recorded post-execution state; preserve conflicts | Local filesystem, SHA-256, append-only ledger |
| Agent Capability Profiles | Declare which agents can perform which capabilities and which evidence/quality axes they require | Versioned YAML + typed loader |
| Scorecard ledger | Derive historical quality signals from eval results; never grant mutation authority | Deterministic local JSONL/JSON projection |
| Runtime Eval Gate | Run declarative golden, holdout and mutation cases against persisted outcomes and required evidence | Existing eval suite plus runtime gate |
| RuntimeExperience facade | Provide one service API for the friendly DX commands and keep presentation thin | Application layer, JSON-serializable results |
| CLI projections | Preserve `runtime ...` expert commands and add friendly top-level projections | Typer delegates to application services |
| Independent verification | Check proofs and receipts independently of the producer and keep unresolved gaps visible | Existing verifier/evidence contracts and test gates |

---

## Key Decisions

### Decision 1: ControlPlane is the single lifecycle authority

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The repository already has a persistent `ControlPlane` with
dependencies, leases, retries, cancellation, review and replay, while the
supervisor and scheduler maintain partially overlapping in-memory state.

**Choice:** Extend `ControlRun`/`ControlStep` additively with stable
idempotency/checkpoint/result references and make the supervisor drive every
step transition through `ControlPlane`. `AgenticRun` is saved as a projection
after the canonical transition.

**Rationale:** This directly satisfies the MUST requirement without creating a
third state machine. Existing expert control commands remain useful and old
TaskSpec run indexes remain readable.

**Alternatives Rejected:**
1. Let the supervisor own a new lifecycle - rejected because resume and CLI
   behavior would diverge from control commands.
2. Replace the existing control model wholesale - rejected because it would
   break persisted artifacts and require an unnecessary migration.

**Consequences:**
- Every worker transition must be explicit and persisted before the next step.
- The scheduler becomes an executor of ready work, not a lifecycle authority.
- A small compatibility adapter is needed for legacy runs without control
  records.

---

### Decision 2: Additive versioning with an explicit compatibility adapter

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** `VersionedContract` uses closed Pydantic models and existing runs
are already persisted under TaskSpec directories.

**Choice:** Add optional fields to the existing version-1 contracts only when
their meaning is unchanged. If a semantic change cannot be additive, create a
version-2 sibling and a loader that reports the source version and migration
status. Never rewrite legacy artifacts during read/resume.

**Rationale:** Loading is safe and deterministic, and a future migration can
be explicit, hashable and independently verified.

**Alternatives Rejected:**
1. Change the version literal in place - rejected because old payloads would no
   longer validate.
2. Silently fill missing proof fields with success - rejected because absence
   of evidence must remain `unresolved`.

**Consequences:** Compatibility tests become a release gate. Legacy runs with
   insufficient state may be projected as `REVIEW` or `BLOCKED`, never `DONE`.

---

### Decision 3: Rollback uses strict compare-and-swap semantics

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** `autonomy/heal.py` snapshots bytes but currently does not stop
   before writing when the target changed after the snapshot.

**Choice:** Record both `pre` and `post` state for every declared writable
   path. A rollback may write only when the current state equals the recorded
   `post` state (or the exact absent state); otherwise it emits
   `AF-HEAL-ROLLBACK-CONFLICT`, preserves the current bytes and snapshot, and
   returns an explicit conflict resolution.

**Rationale:** A digest comparison is the strongest local ownership signal
   available for arbitrary files without claiming process or provider
   ownership. It guarantees that an external change is not overwritten.

**Alternatives Rejected:**
1. Restore whenever the path is declared writable - rejected because this
   destroys concurrent work.
2. Use file timestamps as ownership - rejected because timestamps are not a
   content proof and are not stable across copies.

**Consequences:** A rollback can end in `conflict` and requires reconciliation;
   no automatic merge is attempted. Missing post-state evidence is a named
   refusal, not permission to overwrite.

---

### Decision 4: Routing is evidence-aware, while authorization remains policy-owned

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The public capability matrix already distinguishes supported,
   heuristic, unresolved and unsupported capabilities, while the agentic
   registry currently selects mostly by kind and risk.

**Choice:** Add declarative Agent Capability Profiles and a deterministic
   eligibility filter. The filter excludes `unsupported` records, missing
   prerequisites and profiles lacking required evidence. Scorecards may order
   otherwise eligible agents, but `policy.py` remains the only authorization
   boundary.

**Rationale:** Quality history improves routing without creating an unsafe
   coupling where a high score can authorize a sensitive or external action.

**Alternatives Rejected:**
1. Select agents only by historical score - rejected because score is not a
   capability proof or a policy decision.
2. Treat `unresolved` as supported - rejected because it converts a blind spot
   into a runtime claim.

**Consequences:** Missing evidence can reduce the eligible set to zero and
   must produce `REVIEW`/`BLOCKED` with the unlock named.

---

### Decision 5: Every slice has an independent quality gate

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The existing eval suite is declarative and offline, but the kernel
   evolution needs cases for failure, resume, tool allowlists, conflicts and
   evidence gaps.

**Choice:** Extend the existing case/result shape only additively and add a
   runtime gate requiring mandatory golden, holdout and mutation cases. The
   gate consumes persisted outcomes and evidence; it never calls a model SDK.
   A producer result is not accepted as independent proof of itself.

**Rationale:** This makes quality measurable and repeatable in local CI while
   preserving the project's evidence-first boundary.

**Alternatives Rejected:**
1. Use test pass rate as the only gate - rejected because it misses semantic
   outcomes and evidence completeness.
2. Make external model evaluation a core dependency - rejected because it
   violates offline-first and would make results non-reproducible.

**Consequences:** A slice may finish with visible `REVIEW`/`BLOCKED` status and
   unresolved gaps when its mandatory cases cannot be proven.

---

### Decision 6: Friendly DX is a projection of application services

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The current CLI contains expert runtime commands and the desired
   `doctor`, `status`, `review`, `evolve` and `resume` experience must not grow
   a second set of rules.

**Choice:** Create `RuntimeExperience` application services returning
   canonical JSON-serializable payloads. Add thin top-level Typer commands
   that delegate to those services; keep all existing `runtime ...` commands
   and control-plane commands compatible.

**Rationale:** CLI, future MCP and future UI can share the same projection,
   status vocabulary, gaps and refusal codes.

**Alternatives Rejected:**
1. Put business logic directly in Typer handlers - rejected because it would
   make each surface semantically different.
2. Build a UI before the kernel - rejected by the defined YAGNI boundary.

**Consequences:** The application facade must stay independent of Typer and
   external providers. Output detail level only changes presentation, not
   meaning.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/agentic.py` | Modify | Additive checkpoint, idempotency, profile, scorecard and evidence-reference contracts | @api-agentic-orchestrator | None |
| 2 | `src/apiforge/rules/agent_profiles.yaml` | Create | Declarative agent profiles, required capabilities, evidence and quality axes | @api-governance-reviewer | 1 |
| 3 | `src/apiforge/runtime/registry.py` | Modify | Load profiles and select eligible capabilities deterministically; keep score out of authorization | @api-agentic-orchestrator | 1, 2 |
| 4 | `src/apiforge/capabilities/scorecard.py` | Create | Derive and persist scorecards from eval results without mutation authority | @api-agentic-observability-engineer | 1 |
| 5 | `src/apiforge/runtime/control.py` | Modify | Make the existing control plane canonical for DAG, lease, retry, checkpoint, cancel, resume and idempotent completion | @api-agentic-orchestrator | 1 |
| 6 | `src/apiforge/runtime/scheduler.py` | Modify | Consume ControlPlane-ready steps with bounded parallelism and explicit retry/timeout results | @api-agentic-orchestrator | 5 |
| 7 | `src/apiforge/runtime/store.py` | Modify | Persist atomic projections, event hashes, artifact reuse and normalized replay | @api-agentic-observability-engineer | 1, 5 |
| 8 | `src/apiforge/runtime/supervisor.py` | Modify | Create DAG invocations, drive canonical transitions, reuse completed artifacts and require independent verification | @api-agentic-orchestrator | 3, 5, 6, 7 |
| 9 | `src/apiforge/runtime/runner.py` | Modify | Make resume/review/status use the persisted control run instead of replaying a new run | @api-runtime-migration-planner | 5, 7, 8 |
| 10 | `src/apiforge/autonomy/heal.py` | Modify | Persist post-state and enforce CAS rollback with named conflict outcomes | @api-agentic-orchestrator | 1, 7 |
| 11 | `src/apiforge/capabilities/registry.py` | Modify | Expose public capability state/evidence to the routing filter without changing the matrix source of truth | @api-governance-reviewer | 1, 3 |
| 12 | `src/apiforge/capabilities/verify.py` | Modify | Independently verify profile/matrix prerequisites, limitations, evidence and verifier references | @api-verification-engineer | 2, 11 |
| 13 | `src/apiforge/evals/suite.py` | Modify | Add optional case kind/mandatory metadata and preserve existing case loading | @api-test-strategist | None |
| 14 | `src/apiforge/evals/runtime_gate.py` | Create | Execute deterministic golden/holdout/mutation gate over runtime outcomes and evidence | @api-verification-engineer | 4, 13 |
| 15 | `src/apiforge/application/runtime_experience.py` | Create | Canonical `doctor`, `status`, `review`, `evolve` and `resume` application services | @api-dx-docs-reviewer | 7, 8, 9, 14 |
| 16 | `src/apiforge/cli.py` | Modify | Add thin friendly commands while preserving expert runtime/control commands | @api-dx-docs-reviewer | 15 |
| 17 | `src/apiforge/rules/agentic_runtime.yaml` | Modify | Add profile/eval/resume policy defaults and preserve local-CI-safe limits | @api-governance-reviewer | 2, 3, 14 |
| 18 | `docs/catalog-contract.md` | Modify | Register every new refusal/error code with rejected field and safe unlock | @api-governance-reviewer | 5, 10, 12, 14 |
| 19 | `tests/runtime/test_control_plane.py` | Modify | DAG, idempotent completion, checkpoint and terminal-state proofs | @api-verification-engineer | 5 |
| 20 | `tests/runtime/test_control_leases.py` | Modify | Lease expiration, recovery, ownership and duplicate-result protection | @api-verification-engineer | 5 |
| 21 | `tests/runtime/test_scheduler.py` | Modify | Dependency ordering, timeout, retry, max calls and bounded parallelism | @api-test-strategist | 6 |
| 22 | `tests/runtime/test_supervisor.py` | Modify | Canonical transitions, adaptive review/debate and independent proof gate | @api-agentic-observability-engineer | 8 |
| 23 | `tests/runtime/test_store_replay.py` | Modify | Artifact reuse, atomic projection, replay equivalence and legacy loading | @api-runtime-migration-verifier | 7, 9 |
| 24 | `tests/autonomy/test_heal.py` | Modify | Byte-preserving CAS rollback and concurrent-change conflict | @api-adversarial-critic | 10 |
| 25 | `tests/evals/test_runtime_evals.py` | Modify | Mandatory golden/holdout/mutation gate and scorecard derivation | @api-verification-engineer | 4, 13, 14 |
| 26 | `tests/evals/cases/kernel_evolution.yaml` | Create | Declarative cases for all required runtime failure and evidence axes | @api-test-strategist | 13 |
| 27 | `tests/fixtures/agentic_runtime/kernel_scenarios.yaml` | Create | Offline fixtures for timeout, invalid output, conflict, lease and resume scenarios | @api-adversarial-critic | 26 |
| 28 | `tests/capabilities/test_scorecard.py` | Create | Profile eligibility, score ordering and non-authorization invariant | @api-governance-reviewer | 2, 3, 4 |
| 29 | `tests/application/test_runtime_experience.py` | Create | Canonical friendly-service payloads, states, gaps and refusal codes | @api-dx-docs-reviewer | 15 |
| 30 | `tests/e2e/test_agentic_slice.py` | Modify | End-to-end slice gates and compatibility with existing agentic flow | @api-verification-engineer | 8, 14, 15 |
| 31 | `tests/e2e/test_governance_cli.py` | Modify | Friendly CLI projections and expert-command compatibility | @api-dx-docs-reviewer | 16 |

**Total Files:** 31

The manifest intentionally does not add a provider SDK, infrastructure file,
remote adapter or web/TUI surface. Existing `TaskSpec`, `Policy`, `Brief`,
`Evidence` and public capability contracts remain sources of truth and are
consumed by the files above.

---

## Agent Assignment Rationale

> Agents discovered from the project `agents/` catalog and matched by the
> runtime, evidence, governance and DX responsibilities in the manifest.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @api-agentic-orchestrator | 1, 3, 5, 6, 8, 10 | Owns bounded agentic runtime, TaskSpec, capabilities, handoffs, budgets and policy-governed transitions |
| @api-agentic-observability-engineer | 4, 7, 22 | Owns supervisor observability, artifacts, event trails, debates and verification references |
| @api-runtime-migration-planner | 9 | Designs compatibility-aware resume and migration paths without inventing legacy proof |
| @api-runtime-migration-verifier | 23 | Independently verifies legacy loading, receipts, replay and unresolved compatibility gaps |
| @api-verification-engineer | 12, 14, 19, 20, 25, 30 | Verifies receipts, evidence, capabilities, proof axes and independent release gates |
| @api-adversarial-critic | 24, 27 | Attempts to refute rollback safety, false DONE, stale evidence and excessive agency |
| @api-test-strategist | 13, 21, 26 | Maps acceptance scenarios to deterministic unit, negative, holdout and mutation coverage |
| @api-governance-reviewer | 2, 11, 17, 18, 28 | Owns capability promises, refusal catalog, versioning and policy boundaries |
| @api-dx-docs-reviewer | 15, 16, 29, 31 | Ensures friendly surfaces project canonical states, errors, gaps and examples |
| (general) | None | Every manifest file has a matched project specialist; build coordination remains with the SDD workflow |

**Agent Discovery:**
- Scanned: `agents/**/*.md` in the project and the AgentSpec plugin catalog.
- Matched by: runtime responsibility, evidence boundary, file path, policy
  ownership, testing scope and KB domains `genai`, `python`, `testing`,
  `pydantic` and `component-model`.
- Routing note: `apiforge next-step` was executed against the persisted case;
  it returned `AF-ROUTING-NO-FINDINGS` because the current findings input is
  empty. Specialist assignment therefore follows the explicit SDD design
  manifest and project agent descriptions, not an inferred finding.

---

## Code Patterns

### Pattern 1: Canonical transition through ControlPlane

```python
# The supervisor may execute work, but only ControlPlane changes lifecycle state.
control = ControlPlane(root)
ready = control.ready(run_id)
for step in ready:
    claimed = control.claim(
        run_id,
        step.step_id,
        worker_id=worker_id,
        lease_until=lease_until,
    )
    result = await execute_step(step)
    control.complete(run_id, step.step_id, result)
# AgenticRun is then rebuilt as a projection of control.get(run_id) + artifacts.
```

The actual implementation must preserve the existing `ContractError` codes,
record an event before exposing the next transition and reject a completion
whose idempotency key already has a different result hash.

### Pattern 2: CAS-safe rollback

```python
pre = snapshot_paths(writable_paths)
execute_declared_steps()
post = hash_paths(writable_paths)
persist_json("pre.json", pre)
persist_json("post.json", post)

for path in writable_paths:
    current = hash_or_absent(path)
    if current != post[path]:
        record_conflict(path, expected=post[path], actual=current)
        continue  # never write the snapshot on divergence
    restore_snapshot(path, pre[path])
```

`absent` is a first-class state. Missing post-state or a missing snapshot is a
named refusal and is never treated as permission to restore.

### Pattern 3: Evidence-aware capability selection

```python
eligible = [
    capability
    for capability in public_matrix
    if capability.state != "unsupported"
    and all(item in available_prerequisites for item in capability.prerequisites)
    and all(item in available_evidence for item in profile.required_evidence)
]
ordered = sorted(eligible, key=lambda item: scorecard.rank(item.capability_id))
# `ordered` is a routing proposal; policy.decide(...) still authorizes actions.
```

If no candidate remains, return `unresolved`/`REVIEW` with the missing
prerequisite or evidence reference. Do not fall back to an unsupported
capability.

### Pattern 4: Compatibility loader without silent success

```python
payload = load_json(path)
try:
    run = ControlRun.model_validate(payload)
    compatibility = "native"
except ValidationError:
    run, compatibility = migrate_legacy_run(payload)
if compatibility != "native" and not run_has_required_proof(run):
    status = "REVIEW"
```

The loader may project old data, but it cannot create missing evidence,
approval, independent verification or a successful result hash.

### Pattern 5: Configuration structure

```yaml
runtime:
  default_policy: local-ci-safe
  resume:
    reuse_completed: true
    require_idempotency_key: true
    legacy_without_control: review
  eval_gate:
    required_kinds: [golden, holdout, mutation]
    block_on_missing_evidence: true
  healing:
    rollback_mode: cas_strict
  profiles_file: agent_profiles.yaml
```

Existing limits remain the defaults: `max_parallel_agents=4`, `max_calls=20`,
`max_rounds=3`, `timeout_seconds=120`, `max_retries=2`, and external mutation
disabled. Any policy override is persisted and evaluated by the existing policy
engine.

---

## Data Flow

```text
1. User submits a sealed TaskSpec through an expert or friendly command.
   │
   ▼
2. RuntimeExperience loads the TaskSpec, current run/control record and policy;
   it returns a named refusal when the task is not sealed or inputs are absent.
   │
   ▼
3. Supervisor reviews the task, loads the public capability matrix and agent
   profiles, then creates a deterministic DAG with stable invocation keys.
   │
   ▼
4. ControlPlane persists `planned`, releases ready steps, claims leases and
   records every attempt before the bounded scheduler invokes a worker.
   │
   ▼
5. The adapter returns a typed structured response. The runtime validates it,
   hashes the artifact, persists the artifact/event and completes the step
   idempotently through ControlPlane.
   │
   ▼
6. Resume reopens the persisted run, recovers expired leases, reuses completed
   artifacts with matching hashes and executes only eligible remaining steps.
   │
   ▼
7. Critic/referee/verifier and the runtime eval gate inspect evidence,
   holdouts, mutation probes and policy outcomes independently.
   │
   ▼
8. The outcome projection publishes `DONE` only when required proof exists;
   otherwise it publishes `REVIEW` or `BLOCKED` with gaps and next action.
   │
   ▼
9. `doctor`, `status`, `review`, `evolve` and `resume` render that projection;
   they do not recalculate lifecycle semantics.
```

Self-healing follows a parallel local flow: snapshot declared paths, execute
only policy-dispatchable verbs, record post-state, verify findings, then accept
or rollback. Rollback performs the CAS comparison immediately before any write;
any mismatch ends in conflict without modifying the target.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| Local filesystem (`.apiforge`) | JSON/JSONL persistence for control, tasks, runs, artifacts, receipts and heal snapshots | None; path inputs remain declared and local |
| `ModelAdapter` / `FakeModelAdapter` | Provider-neutral in-process protocol for structured worker responses | None in core; fake adapter is the deterministic default |
| Public capability matrix | Read-only YAML registry for capability state, prerequisites, limitations, evidence and verifier | None |
| Policy engine | In-process decision boundary for tools, autonomy classes and approval gates | None; evidence/approval fields are explicit inputs |
| CLI / future MCP / IDE / UI | Contract projections through `RuntimeExperience` | Surface-specific; no network integration added by this feature |
| Docker Desktop | Optional local test fixture host only | Not required; no production or provider claim |

External GitHub, AWS, database, broker and CI systems remain outside this
feature's write path. Existing read-only adapters and receipts are not widened.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Contracts, profile eligibility, scorecards, CAS hash decisions | `tests/runtime/test_control_plane.py`, `tests/runtime/test_control_leases.py`, `tests/autonomy/test_heal.py`, `tests/capabilities/test_scorecard.py` | pytest, Pydantic models | All new state/error branches, including conflict and absent states |
| Unit | Scheduler ordering, timeout, retry, budget and dynamic parallelism | `tests/runtime/test_scheduler.py` | pytest, fake adapter | AT-001, AT-002, AT-005 and negative dependency paths |
| Integration | Supervisor + ControlPlane + RunStore + TaskStore | `tests/runtime/test_supervisor.py`, `tests/runtime/test_store_replay.py` | pytest, `tmp_path` | AT-003, AT-007, AT-011 with persisted artifacts and replay |
| Eval gate | Golden, holdout, mutation, evidence and adversarial runtime scenarios | `tests/evals/test_runtime_evals.py`, `tests/evals/cases/kernel_evolution.yaml`, `tests/fixtures/agentic_runtime/kernel_scenarios.yaml` | existing offline eval suite | AT-009 and AT-012; mandatory cases block the slice |
| E2E | Full kernel slice plus friendly/expert CLI parity | `tests/e2e/test_agentic_slice.py`, `tests/e2e/test_governance_cli.py`, `tests/application/test_runtime_experience.py` | pytest, Typer runner, local filesystem | AT-004, AT-008, AT-010 and compatibility behavior |
| Static/quality | Code and contract hygiene | entire `src/apiforge`, SDD artifacts | Ruff, mypy strict, spec-linter, `apiforge sdd check`, `git diff --check` | No new lint/type/SDD findings; unresolved behavior remains visible |

Acceptance coverage matrix:

| Acceptance Test | Proof required |
|-----------------|----------------|
| AT-001 | ControlPlane ready set plus scheduler order and parallel bound |
| AT-002 | Expired lease event, re-queued step and no accepted duplicate result |
| AT-003 | Same run/control id, reused artifact hashes and replay-normalized events |
| AT-004 | Terminal `cancelled` state, actor event and no ready work afterward |
| AT-005 | Attempt history, retry bound, max-call refusal and explicit terminal status |
| AT-006 | Changed target remains byte-for-byte unchanged; conflict receipt and snapshot retained |
| AT-007 | Independent verifier/eval gate prevents `DONE` and emits gaps/next action |
| AT-008 | Unsupported/missing-prerequisite capabilities are excluded or unresolved |
| AT-009 | Deterministic cases cover timeout, invalid payload, tool refusal, stale evidence and dissent |
| AT-010 | Friendly commands equal the canonical service payload and preserve expert commands |
| AT-011 | Legacy payloads load/project without mutation; incompatible data is explicit `REVIEW` |
| AT-012 | Mandatory golden/holdout/mutation results are required for slice pass |

The independent verification rule is tested explicitly: the producer's own
artifact is an input to verification, not the verification result itself.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Missing or cyclic dependency | Refuse before dispatch with `AF-RUNTIME-DEPENDENCY`; preserve the plan and unlock | No |
| Timeout or transient adapter failure | Record failed attempt and error code; retry only within step retry and run call budgets | Bounded |
| Invalid adapter payload | Persist the refusal/event as `AF-RUNTIME-SCHEMA`; do not create a successful artifact | No automatic retry unless policy classifies it transient |
| Expired lease | Recover to `pending`, record the recovery event and require a new claim; a completed result remains accepted | Controlled recovery |
| Different result for an existing idempotency key | Refuse with `AF-CONTROL-IDEMPOTENCY-CONFLICT`; preserve both references and block promotion | No |
| Legacy run without sufficient proof | Project as `REVIEW` with `AF-RUNTIME-COMPATIBILITY`; never synthesize proof | No |
| Unsupported capability or missing prerequisite/evidence | Return `unresolved`/`REVIEW` with `AF-CAPABILITY-ELIGIBILITY`; do not fall back silently | No |
| Missing mandatory eval evidence | Return `AF-RUNTIME-EVAL-GATE`; keep failed cases and holdout digest | No |
| Self-healing CAS mismatch | Return `AF-HEAL-ROLLBACK-CONFLICT`; preserve target and snapshot for reconciliation | No |
| Missing post-state/snapshot | Return `AF-HEAL-ROLLBACK-VERSION-UNKNOWN`; refuse to write | No |
| Verification or policy gate failure | Persist `REVIEW`/`BLOCKED`, gaps, missing requirements and next action | No; human/policy action required |

All new refusal codes are added to `docs/catalog-contract.md` with the
rejected field and safe unlock before build is considered complete.

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `runtime.policies.<id>.max_parallel_agents` | int | `4` | Maximum concurrent invocations |
| `runtime.policies.<id>.max_calls` | int | `20` | Total calls per run |
| `runtime.policies.<id>.max_rounds` | int | `3` | Maximum debate/review rounds |
| `runtime.policies.<id>.timeout_seconds` | int | `120` | Per-invocation bounded timeout |
| `runtime.policies.<id>.max_retries` | int | `2` | Per-step retry limit |
| `runtime.policies.<id>.allow_external_mutation` | bool | `false` | Existing safety default; never enabled by profile score |
| `runtime.resume.reuse_completed` | bool | `true` | Reuse only artifacts with matching result/idempotency hashes |
| `runtime.resume.require_idempotency_key` | bool | `true` | Refuse new runtime transitions without stable keys |
| `runtime.resume.legacy_without_control` | enum | `review` | Project legacy runs as `review`, never as proven success |
| `runtime.eval_gate.required_kinds` | list | `[golden, holdout, mutation]` | Mandatory quality evidence for every slice |
| `runtime.eval_gate.block_on_missing_evidence` | bool | `true` | Prevent `DONE` when required evidence is absent |
| `runtime.healing.rollback_mode` | enum | `cas_strict` | Only restore on matching post-state |
| `runtime.profiles_file` | path | `agent_profiles.yaml` | Resource-relative profile registry |

Configuration parsing remains closed and deterministic. Unknown keys fail the
existing policy/registry contract rather than being ignored.

---

## Security Considerations

- External mutation remains disabled by default and is checked by the existing
  policy engine for every action; scorecards cannot bypass that check.
- Tool names, capabilities, writable paths and adapters remain allowlisted;
  model text cannot create a new dispatch route.
- Resume trusts only persisted hashes, typed contracts and receipts. It does
  not trust a model claim that a step completed.
- CAS rollback never writes after a current-state mismatch, protecting
  concurrent local changes and making the conflict visible for review.
- Artifacts and replay events continue to use the existing sensitive-data
  redaction policy; new scorecards store references and aggregate results, not
  raw prompts or secrets.
- A `DONE` projection requires independent verification and mandatory eval
  evidence; unresolved, stale or missing evidence stays visible.
- No network, GitHub, AWS, database or broker mutation is introduced.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured `events.jsonl` records for plan, claim, heartbeat, retry, completion, recovery, conflict, verification and projection; stable event IDs and payload hashes |
| Metrics | Deterministic local aggregates in scorecard/eval projections: attempts, retries, timeouts, evidence completeness, eval score, conflict count and terminal status |
| Tracing | Replay-normalized control and trajectory event streams plus artifact/result hashes; no external tracing service required |

Every terminal result includes status, gaps, evidence references, refusal/error
codes when applicable, and the next safe action. A missing metric is `unresolved`,
not zero.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-23 | design-agent | Initial design from validated DEFINE; ControlPlane authority, CAS rollback, quality gates and canonical DX |
| 1.1 | 2026-09-23 | ship-agent | Shipped and archived after implementation and verification |

---

## Next Step

**Archived:** feature shipped on 2026-09-23; implementation and verification evidence are preserved in the archive.
