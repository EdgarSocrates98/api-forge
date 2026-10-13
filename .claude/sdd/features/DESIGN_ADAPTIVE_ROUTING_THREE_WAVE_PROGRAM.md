# DESIGN: Adaptive Routing Three-Wave Program

> Arquitetura para transformar o ranking de capacidades em um plano de execução
> determinístico, com scorecards multidimensionais e expertise packs reutilizáveis.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM` |
| **Date** | 2026-09-24 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM.md](./DEFINE_ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM.md) |
| **Status** | Ready for Build |

## Architecture Overview

```text
TaskSpec
   |
   v
RoutingRequest -- policy + registry + scorecards + expertise --> RoutingDecision
                                                                     |
                                                                     v
                                                                RoutingPlan
                                                     /        |        \\
                                                primary   parallel   review roles
                                                     \\        |        /
                                                      ControlPlane
                                                           |
                              bounded scheduler + replay + evidence store
                                                           |
                                  eval gate -> scorecard -> freshness -> feedback
                                                           |
                                           future waves / reusable expertise
```

The existing `RoutingDecision` remains the compatibility boundary for ranking
and persisted `routing.json`. `RoutingPlan` is additive and becomes the
execution boundary in `routing-plan.json`; legacy callers can continue to read
the decision without understanding execution roles. The supervisor is the only
component that turns a plan into control steps. Registry, scorecards, evals and
knowledge packs provide facts but do not execute agents or mutate external hosts.

## Components

| Component | Responsibility | Existing/new |
|-----------|----------------|--------------|
| `RoutingPolicy` | Objective order, execution mode and fallback budget | Extend contract |
| `RoutingDecision` | Eligible candidates, ranking and unresolved evidence | Preserve |
| `RoutingPlan` | Primary, fallbacks, parallel reviewers, critic and referee | New v1 contract |
| Capability registry | Capability family, implementation and expertise metadata | Extend loader |
| Supervisor/ControlPlane | Execute initial roles, activate fallbacks, skip unused steps | Extend runtime |
| Scorecard/eval gate | Aggregate dimensions, adversarial evidence and freshness | Extend contracts/runtime |
| Knowledge loader | Validate and expose expertise packs without auto-refresh | Extend contract |
| Store | Persist decision, plan, evidence and replay artifacts | Extend store |
| CLI/docs | Explain plans, evidence, install-independent operation and limits | Extend projection |

## Key Decisions

### Decision 1: `RoutingPlan` is additive to `RoutingDecision`

**Choice:** Keep ranking in `RoutingDecision` and derive a stable `RoutingPlan`
with explicit role collections. `fallback_order` is retained for old clients,
but the supervisor no longer interprets every ranked candidate as a fallback.

**Rationale:** This avoids breaking persisted artifacts and makes the semantic
difference between parallel review and sequential failover inspectable.

**Alternatives rejected:** Reusing `fallback_order` as an overloaded execution
instruction; introducing a second independent router in the supervisor.

### Decision 2: Parallel review is the backward-compatible default

**Choice:** Default `execution_mode` to `parallel_review`, preserving current
multi-specialist review behavior. `sequential_failover` is explicit policy and
only activates fallback candidates after a primary failure.

**Rationale:** Existing conflict/debate behavior depends on independent specialist
results. A silent switch to one-at-a-time execution would change outcomes and
reduce evidence.

### Decision 3: Role assignment is deterministic and bounded

**Choice:** Role assignment uses capability kind and stable registry order:
primary is the selected candidate; reviewers, critic and referee keep their
declared roles; other eligible specialists are parallel or fallback according
to policy. Duplicate role membership is rejected by the contract.

**Rationale:** No model inference is required to decide who runs. `max_fallbacks`
limits work and all plan identifiers are hashes of canonical inputs.

### Decision 4: Unknown and stale evidence remain visible

**Choice:** Missing observations are `unknown`/`unresolved`, stale observations
cannot improve a promoted scorecard, and observed values require evidence refs.
Legacy contracts default to backward-compatible `unknown` freshness.

**Rationale:** The runtime must not silently convert absence or age into quality.
Freshness is a gate on promotion, not a reason to delete history.

### Decision 5: Expertise packs are local, declarative and non-mutating

**Choice:** Expertise packs are loaded from configured repository/packaged paths,
validated with source and freshness metadata, and selected through explicit
capability requirements. Remote refresh, symlinks and host-file overwrites stay
out of scope as previously deferred.

**Rationale:** This preserves offline-first operation and allows a host without
the API Forge runtime to still use copied agents/skills and manifests.

## Data Model Changes

### `RoutingPlan` v1

```text
plan_id, decision_id, task_id, revision
primary: capability | null
fallbacks: ordered tuple[capability]
parallel: ordered tuple[capability]
reviewers: ordered tuple[capability]
critic: capability | null
referee: capability | null
execution_mode: parallel_review | sequential_failover
max_fallbacks: non-negative integer
evidence, unresolved
```

The contract rejects duplicate capabilities across role fields and rejects a
fallback budget that exceeds the declared list. It is frozen, versioned and
uses the existing `AF-*` error/refusal conventions.

### Candidate and registry metadata

Candidate assessments gain family, implementation and expertise-pack metadata.
Registry entries may declare a shared `family`, an `implementation` identifier
and required `expertise_packs`; missing metadata keeps existing behavior.

### Scorecards and signals

Scorecards gain optional dimension scores, observation timestamps/expiry,
freshness state and observed token cost. Existing scalar quality/cost/duration
fields remain readable. `ObservedSignal` gains optional freshness metadata with
legacy defaults.

### Expertise packs

The new versioned contract identifies `pack_id`, domain, version, source refs,
freshness, limitations and evidence level. It does not fetch, rewrite or
symlink host files.

## Code Patterns

- Contracts are frozen Pydantic models with `version: Literal[1]`, additive
  optional fields and `extra="forbid"`; invalid role combinations fail at the
  boundary with an actionable `AF-*` message.
- Runtime functions are pure where possible: canonical payloads feed stable
  IDs, candidate ordering and plan derivation. Persistence happens through the
  existing store, never from a registry or model adapter.
- Control transitions are explicit (`start`, `complete`, `fail`, `skip`) and
  preserve prior errors, evidence and unresolved gaps. Fallback activation is
  bounded by policy and never inferred from prose.
- Legacy JSON and YAML fields retain defaults. New fields must be optional or
  have a deterministic migration path, with focused compatibility tests.
- External integrations remain read-only adapters; no model SDK, network fetch,
  host synchronization or automatic update belongs in the core runtime.

## Execution Flow

1. Build a `RoutingRequest` from `TaskSpec`, policy, available evidence and
   optional required expertise.
2. Assess and rank candidates. Eligibility rejects missing evidence, risk,
   disabled capabilities and unavailable expertise with an explicit unlock.
3. Derive and persist `RoutingPlan` from the decision and registry metadata.
4. Create control steps for the plan. Start primary plus parallel/review roles
   when policy is `parallel_review`; leave fallbacks pending.
5. Complete, fail or skip steps through `ControlPlane`. On primary failure,
   activate fallbacks in deterministic order up to `max_fallbacks`; on success,
   mark unused fallbacks skipped with an auditable reason.
6. Persist invocations, artifacts, events and replay data. Feed only eval-gated,
   evidence-backed observations into scorecards.
7. Expose freshness, unresolved evidence, role decisions and gaps in CLI/JSON and
   bilingual user documentation.

## File Manifest

### Wave 1 — execution semantics

- `src/apiforge/contracts/routing.py`
- `src/apiforge/runtime/routing.py`
- `src/apiforge/runtime/registry.py`
- `src/apiforge/runtime/control.py`
- `src/apiforge/runtime/supervisor.py`
- `src/apiforge/runtime/store.py`
- `tests/runtime/test_routing_plan.py`

### Wave 2 — evaluation and freshness

- `src/apiforge/contracts/agentic.py`
- `src/apiforge/runtime/feedback.py`
- `src/apiforge/runtime/routing.py`
- `src/apiforge/capabilities/scorecard.py`
- `src/apiforge/evals/runtime_gate.py`
- `tests/runtime/test_scorecard_freshness.py`
- `tests/evals/test_adversarial_gate.py`

### Wave 3 — expertise and implementations

- `src/apiforge/contracts/knowledge.py`
- `src/apiforge/contracts/__init__.py`
- `src/apiforge/knowledge/loader.py`
- `src/apiforge/runtime/registry.py`
- `src/apiforge/runtime/routing.py`
- `src/apiforge/rules/agentic_runtime.yaml`
- `tests/runtime/test_expertise_routing.py`
- bilingual user guides and evolution roadmap

## Testing Strategy

| Layer | Proof |
|-------|-------|
| Contract | valid roles, duplicate-role refusal, legacy defaults |
| Routing | deterministic plan IDs, primary/fallback/parallel role mapping |
| Control | unused fallback skip, bounded activation, resume/replay |
| Evaluation | golden/holdout/mutation/adversarial required kinds |
| Freshness | observed, unknown, stale and unresolved promotion behavior |
| Expertise | family/implementation selection and missing-pack refusal |
| Regression | existing runtime, eval, capability and CLI suites |

Every wave must leave a green focused test set and a commit. Final verification
also runs the full suite, Ruff, mypy and the repository SDD/release checks.

## Failure and Safety Semantics

- No eligible primary: preserve `AF-CAPABILITY-ELIGIBILITY` and unresolved gaps;
  do not invent a capability.
- Missing expertise: refuse the candidate with field and safe unlock.
- Primary failure: activate only bounded, explicit fallbacks; preserve the error.
- Stale or evidence-free observation: block promotion and preserve the receipt.
- Invalid pack or unsupported host: remain local/read-only and expose an
  `AF-*` refusal; never silently mutate host state.

## Observability and Compatibility

Plans, role assignment, skipped fallback reasons, freshness state, evidence refs,
hashes and unresolved gaps are persisted in existing run artifacts. `routing.json`
remains valid; `routing-plan.json` is additive. CLI JSON remains machine-readable,
and user docs describe both Portuguese and English workflows.

## Deferred Work

The following remain explicitly after ship: autonomous high-level `ask/improve/
migrate/fix`; complete inference across repository types; separate `apiforge here`;
auto-update and remote knowledge-pack updates; symlink installation; automatic
host-file overwrite synchronization; task-level precedence; distributed
workspace debate; and a promise of total host parity.

## Build Handoff

Implement in three bounded waves, committing after each wave. Do not add remote
mutation or host-specific SDK calls. After Wave 3, run independent verification,
update the build report and bilingual docs, push the existing branch and update
the existing open PR rather than creating a duplicate.
