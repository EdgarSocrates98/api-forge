# DESIGN: API Forge Observability Control Plane

> Technical design for implementing the provider-neutral observability control plane with OTel, Datadog and Dynatrace capabilities.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_OBSERVABILITY_CONTROL_PLANE |
| **Date** | 2026-09-22 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_OBSERVABILITY_CONTROL_PLANE.md](./DEFINE_API_FORGE_OBSERVABILITY_CONTROL_PLANE.md) |
| **Status** | ✅ Shipped |
| **Design Confidence** | 0.95 |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                    API FORGE OBSERVABILITY CONTROL PLANE                     │
├──────────────────────────────────────────────────────────────────────────────┤
│  Inputs                                                                     │
│  [Runtime events] [OTLP/JSON] [Datadog export/API] [Dynatrace export/API]   │
│  [CloudWatch/X-Ray] [AWS/K8s/VM manifests] [OpenAPI + source adapters]      │
│                                      │                                       │
│                                      ▼                                       │
│  Source adapters → redaction/allowlist → canonical telemetry contracts      │
│                                      │                                       │
│                                      ▼                                       │
│  Snapshot + provenance + graph edges + token/economy accounting             │
│                                      │                                       │
│                                      ▼                                       │
│  RED/USE + SLO/error-budget/burn-rate + cardinality + drift + cost engine   │
│                                      │                                       │
│                                      ▼                                       │
│  Agent team: discovery → SLO/perf → vendor → security → dashboard/critic    │
│                                      │                                       │
│                                      ▼                                       │
│  debate/referee → canonical intent → vendor projection → deterministic diff│
│                                      │                                       │
│                                      ▼                                       │
│  dry-run → policy/approval → broker credential → apply → verify → rollback  │
│                                      │                                       │
│                                      ▼                                       │
│  receipts, audit ledger, replay, brief DONE/REVIEW/BLOCKED                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

The control plane is a library-first local/CI subsystem. The canonical model,
analysis and planning layers never import Datadog, Dynatrace, AWS or cloud
credential SDKs. Vendor and environment adapters implement protocols behind
explicit capability declarations. External mutation is a separate governed
boundary and is disabled unless a policy, credential reference, approval and
rollback plan are all present.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Canonical telemetry contracts | Versioned resource, service, endpoint, trace, span, metric, log, event, SLO, finding, intent, diff and receipt schemas | Pydantic v2, `contracts/base.py`, JSON-compatible values |
| Source adapter registry | Load and select `otel-json`, runtime, Datadog, Dynatrace, CloudWatch/X-Ray and environment discovery adapters | Protocols, YAML registry, lazy imports |
| Redaction and cardinality guard | Enforce attribute allowlists, secret/PII redaction, route normalization and bounded dimensions | Pure Python, policy YAML, deterministic diagnostics |
| Telemetry normalizer | Convert source-specific exports to canonical records with provenance and source hashes | Existing `CodeInventory`/fact patterns plus observability contracts |
| Snapshot/provenance store | Persist observed state, desired state, graph links, hashes and replay material | `.apiforge/observability/`, JSONL/JSON, graphify edges |
| Signal analysis engine | Compute RED/USE, percentiles, TPS observed, saturation, availability, SLO, error budget, burn rate, cardinality and gaps | Deterministic functions over canonical records |
| Desired-state planner | Produce monitor, SLO, dashboard, query, event and deployment-marker intents | Pydantic intents, vendor-neutral fields, explicit unsupported capabilities |
| Vendor projection adapters | Project canonical intents to Datadog and Dynatrace schemas and compare observed/desired state | Adapter protocols; HTTP clients remain optional integration extras |
| Drift/diff engine | Compare normalized snapshots and vendor projections; never infer equivalence | Canonical hashing, stable sorted diffs |
| Agentic observability team | Route discovery, SLO, performance, vendor, dashboard, security and evaluation work | Existing Runtime Agentico 2.0, TaskSpec, debate, critic and referee |
| Governance executor | Perform dry-run, approval, broker lookup, apply, verify and rollback receipt | Existing policy/autonomy boundaries plus new intent gates |
| CLI/MCP surface | Expose discover, ingest, analyze, plan, diff, apply, verify and capabilities with parity | Typer and MCP tool registry |
| Fixture/eval suite | Simulate vendors, environments, failures, drift, cardinality and safety refusals | pytest, YAML/JSON fixtures, structural evals |

---

## Key Decisions

### Decision 1: Canonical OTel-aligned model with vendor projections

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** OTel provides common semantic conventions, while Datadog and
Dynatrace expose valuable but different native concepts. A vendor-first model
would make agents, tests and policies diverge.

**Choice:** Define versioned API Forge contracts aligned with OTel resources,
traces, spans, metrics and logs. Add vendor-specific fields only inside typed
capability payloads and projections. Preserve original query/entity/monitor
references as redacted provenance.

**Rationale:** The repository already has an OTel JSON adapter, `PerformanceRun`,
fact provenance and replay conventions. OpenTelemetry defines semantic
conventions for traces and related signals; Dynatrace documents OTel ingestion
with optional enhanced native features; Datadog and Dynatrace can therefore be
consumers of the same normalized evidence without pretending to be identical.

**Alternatives Rejected:**
1. Native vendor model as the core — rejected because it creates lock-in and
   makes Java/Go/Python and multi-environment support asymmetric.
2. Lowest-common-denominator fields only — rejected because monitors, SLOs,
   dashboards, queries and deployment markers need native capabilities.

**Consequences:**
- Every adapter must report supported, unsupported and lossy fields.
- Cross-vendor comparison is evidence-bound and may end in `INCONCLUSIVE`.
- The canonical model remains stable when a vendor API evolves.

### Decision 2: Control plane as a pure plan/apply boundary

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The user selected multi-environment autonomy, but external vendor
mutation is high-risk and credentials are not available in CI.

**Choice:** Separate `observe/normalize/analyze/plan/diff` from `apply/verify`.
The first group is read-only and deterministic. Apply requires a capability,
environment policy, credential reference, dry-run result, diff, approval and
rollback reference. Each operation emits a receipt and is independently verified.

**Rationale:** This matches API Forge policy, TaskSpec, evidence and approval
patterns and directly addresses excessive agency, secret exposure and vendor
drift. It also makes fake adapters useful without weakening production gates.

**Alternatives Rejected:**
1. Agent can call vendor APIs after generating a recommendation — rejected
   because model text is not authorization.
2. Always read-only — rejected because the selected MVP includes governed
   monitors, SLOs, dashboards, events and deployment markers.

**Consequences:**
- A normal local/CI run ends in `DONE`, `REVIEW` or `BLOCKED` based on evidence;
  it does not imply that a vendor was changed.
- Broker and live vendor adapters are optional extras and never core imports.

### Decision 3: Capability matrix instead of artificial parity

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Datadog and Dynatrace have different SLO, query, entity, monitor,
dashboard and alert semantics.

**Choice:** Each adapter publishes capabilities with operation, mode,
environment, auth scope, rate limit, mutability, lossiness and verification
requirements. A planner can choose a common intent, a vendor extension or
return `unsupported`/`inconclusive`.

**Rationale:** Explicit asymmetry is safer than silently translating a DQL
entity selector into a Datadog query or the reverse. It also gives agents a
closed vocabulary for routing and debate.

**Alternatives Rejected:**
1. Pretend both vendors implement the same interface — rejected because it
   hides semantic differences and creates false DONE.
2. Duplicate every planner for every vendor — rejected because shared evidence,
   policy and testing would drift.

### Decision 4: Snapshot state plus graph provenance

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Drift, impact analysis and incident reasoning require historical
observed state, desired state and relationships among services, endpoints,
deployments, databases, agents and evidence.

**Choice:** Persist immutable observation snapshots and desired-state plans with
content hashes, then emit graphify edges for `observed`, `depends_on`,
`produced_by`, `violates`, `impacts` and `verified_by` relationships.

**Rationale:** It reuses the project's graph and evidence model without making
the graph the source of truth. A canonical JSON snapshot remains replayable and
portable; graph queries provide navigation and impact views.

**Consequences:** Snapshot retention and sensitive-attribute redaction must be
policy-driven. Graph updates are derived and must never mutate vendor state.

### Decision 5: Deterministic statistical analysis with explicit inconclusive

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The system must report p99, TPS and SLO outcomes without inventing
capacity or causality from incomplete telemetry.

**Choice:** Use deterministic nearest-rank percentiles, explicit sample counts,
source/environment identity, generator/downstream validity checks and an
`INCONCLUSIVE` result whenever evidence is insufficient.

**Rationale:** This extends existing `PerformanceRun` and capacity-agent rules:
received requests are not completed TPS, and a saturated generator or missing
downstream signal invalidates a strong conclusion.

**Alternatives Rejected:**
1. LLM-estimated performance — rejected because observations must be measured.
2. Always return a numeric SLO verdict — rejected because missing data must be
   visible rather than converted into confidence.

### Decision 6: Fixtures before live tenants

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** There are no real Datadog/Dynatrace exports or credentials today.

**Choice:** Build fake/replay adapters, synthetic exports and contract fixtures
that model valid, invalid, partial, rate-limited, drifted and high-cardinality
responses. Live adapters are tested only behind optional integration markers.

**Rationale:** CI remains offline, deterministic and safe while the contract and
capability matrix can evolve. Real anonymized samples can be added later without
changing the test architecture.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/observability.py` | Create | Canonical telemetry, SLO, finding, intent, diff, capability, credential and receipt contracts | @api-observability-control-plane | `contracts/base.py`, `core/models.py` |
| 2 | `src/apiforge/contracts/registry.py` | Modify | Register observability contracts and schemas | @api-observability-control-plane | 1 |
| 3 | `docs/contracts/Observability-telemetry-invariants.md` | Create | Document canonical signal and provenance invariants | @api-dx-docs-reviewer | 1 |
| 4 | `docs/contracts/Observability-intent-invariants.md` | Create | Document desired-state intent, diff and approval semantics | @api-dx-docs-reviewer | 1 |
| 5 | `docs/contracts/Observability-receipt-invariants.md` | Create | Document apply/verify/rollback receipts | @api-dx-docs-reviewer | 1 |
| 6 | `src/apiforge/observability/__init__.py` | Create | Public control-plane API | @api-observability-control-plane | 1, 7 |
| 7 | `src/apiforge/observability/protocols.py` | Create | Source, vendor, credential and operation protocols | @api-vendor-integration-engineer | 1 |
| 8 | `src/apiforge/observability/registry.py` | Create | Load adapters and capability matrix | @api-vendor-integration-engineer | 7, 9 |
| 9 | `src/apiforge/rules/observability_control_plane.yaml` | Create | Policies, redaction, cardinality, environments and gates | @api-observability-security-engineer | 1, 7 |
| 10 | `src/apiforge/observability/redaction.py` | Create | Attribute allowlist, PII/secret redaction and route normalization | @api-observability-security-engineer | 9 |
| 11 | `src/apiforge/observability/normalize.py` | Create | Normalize all source records into canonical contracts | @api-telemetry-normalization-engineer | 1, 7, 10 |
| 12 | `src/apiforge/observability/snapshot.py` | Create | Immutable snapshots, hashes, retention and replay inputs | @api-observability-control-plane | 1, 11 |
| 13 | `src/apiforge/observability/provenance.py` | Create | Evidence and graphify edge projection | @api-observability-control-plane | 1, 12 |
| 14 | `src/apiforge/observability/signals.py` | Create | RED/USE, percentiles, throughput, saturation and gaps | @api-capacity-engineer | 1, 11 |
| 15 | `src/apiforge/observability/slo.py` | Create | SLI, SLO, error budget and burn-rate evaluation | @api-slo-reliability-engineer | 1, 14 |
| 16 | `src/apiforge/observability/cardinality.py` | Create | Cardinality budgets, dimensions and findings | @api-observability-security-engineer | 1, 10, 11 |
| 17 | `src/apiforge/observability/drift.py` | Create | Observed/desired snapshot comparison and stable diffs | @api-drift-reconciliation-engineer | 1, 12 |
| 18 | `src/apiforge/observability/intents.py` | Create | Vendor-neutral monitor/SLO/dashboard/event intents | @api-slo-reliability-engineer | 1, 15, 17 |
| 19 | `src/apiforge/observability/plan.py` | Create | Plan graph, risk classification and proof axes | @api-observability-control-plane | 18, 22 |
| 20 | `src/apiforge/observability/governance.py` | Create | Dry-run, approval, credential reference, apply and rollback gates | @api-observability-security-engineer | 9, 18, 19 |
| 21 | `src/apiforge/observability/adapters/otel_json.py` | Create | Reuse/extend OTLP JSON ingestion into canonical telemetry | @api-telemetry-normalization-engineer | 11, existing `adapters/otel` |
| 22 | `src/apiforge/observability/adapters/runtime.py` | Create | Convert Runtime Agentico trajectory into telemetry | @api-agentic-observability-engineer | 11, existing runtime |
| 23 | `src/apiforge/observability/adapters/datadog.py` | Create | Datadog export/query/projection/apply boundary and capabilities | @api-datadog-integration-engineer | 7, 18, 20 |
| 24 | `src/apiforge/observability/adapters/dynatrace.py` | Create | Dynatrace export/query/projection/apply boundary and capabilities | @api-dynatrace-integration-engineer | 7, 18, 20 |
| 25 | `src/apiforge/observability/adapters/aws.py` | Create | CloudWatch/X-Ray and AWS environment discovery bridge | @aws-api-infra-reviewer | 7, existing AWS dumps |
| 26 | `src/apiforge/observability/adapters/kubernetes.py` | Create | Kubernetes discovery and metadata bridge | @api-architecture-reviewer | 7 |
| 27 | `src/apiforge/observability/adapters/vm.py` | Create | Host/VM discovery metadata bridge | @api-architecture-reviewer | 7 |
| 28 | `src/apiforge/observability/instrumentation.py` | Create | Java/Go/Python OTel guidance and artifact generation | @api-instrumentation-engineer | 1, 11 |
| 29 | `src/apiforge/observability/supervisor.py` | Create | Orchestrate control-plane phases through Runtime Agentico | @api-agentic-observability-engineer | 19, 20, existing runtime |
| 30 | `src/apiforge/observability/verify.py` | Create | Verify receipts, diffs, state and proof axes | @api-verification-engineer | 12, 17, 20 |
| 31 | `src/apiforge/cli.py` | Modify | Add `observability discover|ingest|analyze|plan|diff|capabilities|apply|verify` | @api-agentic-observability-engineer | 29 |
| 32 | `src/apiforge/mcp/tools.py` | Modify | Expose control-plane operations with CLI parity | @api-agentic-observability-engineer | 29, 31 |
| 33 | `src/apiforge/graph/build.py` | Modify | Add canonical observability edge projection | @api-observability-control-plane | 13 |
| 34 | `src/apiforge/brief/render.py` | Modify | Render observability findings, intent and governed apply status | @api-release-guardian | 19, 30 |
| 35 | `src/apiforge/rules/playbooks.yaml` | Modify | Add observability control-plane playbooks | @api-observability-control-plane | 29 |
| 36 | `src/apiforge/rules/routing.yaml` | Modify | Route observability phases and dominant areas to specialists | @api-planner | 35 |
| 37 | `agents/api-observability-control-plane.md` | Create | Coordinator role for discovery, normalization, planning and gates | @api-observability-control-plane | 35, 36 |
| 38 | `agents/api-telemetry-normalization-engineer.md` | Create | Source normalization, provenance and schema gaps | @api-telemetry-normalization-engineer | 11, 21 |
| 39 | `agents/api-vendor-integration-engineer.md` | Create | Shared vendor protocol and capability matrix | @api-vendor-integration-engineer | 7, 8 |
| 40 | `agents/api-datadog-integration-engineer.md` | Create | Datadog native projection and verification | @api-datadog-integration-engineer | 23 |
| 41 | `agents/api-dynatrace-integration-engineer.md` | Create | Dynatrace native projection and verification | @api-dynatrace-integration-engineer | 24 |
| 42 | `agents/api-slo-reliability-engineer.md` | Create | SLI/SLO/error budget/burn rate and reliability plans | @api-slo-reliability-engineer | 15, 18 |
| 43 | `agents/api-observability-security-engineer.md` | Create | Redaction, cardinality, credential and mutation safety | @api-observability-security-engineer | 9, 10, 20 |
| 44 | `agents/api-drift-reconciliation-engineer.md` | Create | Desired/observed state, drift and rollback planning | @api-drift-reconciliation-engineer | 17, 20 |
| 45 | `agents/api-instrumentation-engineer.md` | Create | OTel artifacts and framework-specific guidance | @api-instrumentation-engineer | 28 |
| 46 | `agents/api-agentic-observability-engineer.md` | Create | Runtime supervisor and observability agent team orchestration | @api-agentic-observability-engineer | 29 |
| 47 | `tests/observability/test_contracts.py` | Create | Contract validation and registry | @api-test-strategist | 1, 2 |
| 48 | `tests/observability/test_redaction.py` | Create | PII, secrets, route and allowlist behavior | @api-observability-security-engineer | 10 |
| 49 | `tests/observability/test_normalize.py` | Create | OTel/runtime/vendor canonical normalization | @api-telemetry-normalization-engineer | 11, 21–24 |
| 50 | `tests/observability/test_signals.py` | Create | RED/USE, percentiles, TPS and saturation validity | @api-capacity-engineer | 14 |
| 51 | `tests/observability/test_slo.py` | Create | SLO, error budget and burn-rate cases | @api-slo-reliability-engineer | 15 |
| 52 | `tests/observability/test_capabilities.py` | Create | Vendor/environment capability matrix | @api-vendor-integration-engineer | 8, 23–27 |
| 53 | `tests/observability/test_intents.py` | Create | Monitor/SLO/dashboard/event intents and stable diffs | @api-slo-reliability-engineer | 18 |
| 54 | `tests/observability/test_governance.py` | Create | Dry-run, approval, credentials, apply and rollback gates | @api-observability-security-engineer | 20 |
| 55 | `tests/observability/test_drift.py` | Create | Observed/desired drift and receipts | @api-drift-reconciliation-engineer | 17, 30 |
| 56 | `tests/observability/test_runtime_instrumentation.py` | Create | Runtime trajectory to canonical telemetry | @api-agentic-observability-engineer | 22, 29 |
| 57 | `tests/observability/test_interfaces.py` | Create | CLI/MCP parity | @api-dx-docs-reviewer | 31, 32 |
| 58 | `tests/observability/test_observability_vertical_slice.py` | Create | Offline end-to-end control-plane flow | @api-test-strategist | 11–32 |
| 59 | `tests/fixtures/observability/` | Create | Synthetic OTel, Datadog, Dynatrace, AWS, K8s, VM and failure fixtures | @api-test-strategist | None |
| 60 | `tests/evals/test_observability_evals.py` | Create | Routing, evidence, safety, vendor and SLO evals | @api-evaluation-engineer | 37–46 |
| 61 | `tests/evals/cases/observability_cases.yaml` | Create | At least 12 declarative evaluation cases | @api-evaluation-engineer | 60 |
| 62 | `evals/skills/evals.json` | Modify | Register observability control-plane evals | @api-evaluation-engineer | 60, 61 |
| 63 | `docs/catalog-contract.md` | Modify | Document contracts, adapters, capabilities and AF error codes | @api-dx-docs-reviewer | 1, 7, 20 |
| 64 | `scripts/check_release.py` | Modify | Validate observability contracts, agent mirrors, fixtures and safety boundaries | @api-release-guardian | 1, 37–46 |
| 65 | `agents/api-verification-engineer.md` | Create | Independent verification of receipts, diffs, evidence and proof axes | @api-verification-engineer | 30 |

**Total Files:** 65

---

## Agent Assignment Rationale

> Agents discovered from `agents/**/*.md`. New specialist profiles are part of
> this design and must be mirrored under `.agents/agents/` and `.claude/agents/`.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @api-observability-control-plane | 1–6, 12–13, 19, 33, 35, 37 | Coordinates canonical model, snapshots, graph projection and playbooks. |
| @api-telemetry-normalization-engineer | 11, 21, 38, 49 | Owns source schemas, normalization and provenance gaps. |
| @api-vendor-integration-engineer | 7–8, 39, 52 | Owns protocol boundary and capability matrix. |
| @api-datadog-integration-engineer | 23, 40 | Owns Datadog native semantics, projections and verification. |
| @api-dynatrace-integration-engineer | 24, 41 | Owns Dynatrace entities, DQL/SLO and verification. |
| @api-slo-reliability-engineer | 15, 18, 42, 51, 53 | Owns SLI/SLO, error budgets, intents and reliability thresholds. |
| @api-observability-security-engineer | 9–10, 16, 20, 43, 48, 54 | Owns redaction, cardinality, credentials, tools and mutation gates. |
| @api-drift-reconciliation-engineer | 17, 44, 55 | Owns desired/observed comparison, drift and rollback planning. |
| @api-capacity-engineer | 14, 50 | Existing specialist matches measured latency, TPS and validity rules. |
| @api-agentic-observability-engineer | 22, 29, 31–32, 46, 56 | Coordinates Runtime Agentico integration and host interfaces. |
| @api-instrumentation-engineer | 28, 45 | Produces Java/Go/Python OTel guidance and artifacts. |
| @aws-api-infra-reviewer | 25 | Existing AWS specialist matches CloudWatch/X-Ray and environment posture. |
| @api-architecture-reviewer | 26–27 | Existing architecture specialist matches Kubernetes and VM topology. |
| @api-dx-docs-reviewer | 3–5, 57, 63 | Contract/API documentation and CLI/MCP parity. |
| @api-test-strategist | 47, 58–59 | Test matrix, fixtures and vertical slice. |
| @api-evaluation-engineer | 60–62 | Existing eval conventions plus new structural cases. |
| @api-verification-engineer | 30 | Independent receipt, diff and proof verification. |
| @api-release-guardian | 34, 64 | Release contracts, brief and gate integrity. |
| @api-planner | 36 | Existing routing specialist matches phase/area selection. |

**Agent Discovery:**
- Scanned: `agents/**/*.md` and existing host mirrors.
- Matched by: observability, performance, runtime, security, SLO, vendor,
  AWS, architecture, testing, evaluation and release responsibilities.
- New profiles are required because Datadog/Dynatrace projections,
  normalization, drift and control-plane safety are distinct responsibilities.

---

## Code Patterns

### Pattern 1: Provider-neutral adapter protocol

```python
from collections.abc import Mapping
from typing import Protocol

from apiforge.contracts.observability import CapabilitySet, ObservationSnapshot


class ObservabilityAdapter(Protocol):
    name: str

    def capabilities(self) -> CapabilitySet:
        ...

    def observe(self, request: Mapping[str, object]) -> ObservationSnapshot:
        ...

    def plan(self, intent: Mapping[str, object]) -> Mapping[str, object]:
        ...

    def apply(self, plan: Mapping[str, object], credential_ref: str) -> Mapping[str, object]:
        ...
```

Use this boundary for OTel, Datadog, Dynatrace, AWS, Kubernetes and VM
adapters. The core imports the protocol, not a vendor SDK. `apply` is never
called by analysis code; the governance service decides whether it is eligible.

### Pattern 2: Immutable canonical contract with provenance

```python
from pydantic import Field

from apiforge.contracts.base import VersionedContract


class CanonicalSpan(VersionedContract):
    trace_id: str
    span_id: str
    service_name: str
    operation: str
    duration_ms: float = Field(ge=0)
    status: str
    attributes: dict[str, str] = Field(default_factory=dict)
    source: str
    source_sha256: str
    observed_at: str
```

Contracts must reject unknown fields, freeze nested JSON where required and
carry source/hash/provenance. Vendor payloads are preserved only in a redacted
capability envelope, never as an unbounded raw blob.

### Pattern 3: Redaction before persistence or export

```python
def sanitize_attributes(
    attributes: Mapping[str, object],
    *,
    allowed: frozenset[str],
    sensitive: frozenset[str],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in attributes.items():
        if key not in allowed or key in sensitive:
            continue
        result[key] = str(value)[:256]
    return result
```

Apply the guard before hashing, writing events, creating graph edges or calling
a vendor. Route templates must replace path identifiers before cardinality
analysis. Raw headers, tokens, bodies, query values and user identifiers are
denied by default.

### Pattern 4: Capability-aware intent and diff

```python
def plan_intent(adapter: ObservabilityAdapter, intent: ObservabilityIntent) -> PlanResult:
    capability = adapter.capabilities().for_intent(intent.kind, intent.environment)
    if not capability.supported:
        return PlanResult.inconclusive("vendor capability is unsupported")
    projection = adapter.plan(intent.model_dump(mode="json"))
    return stable_diff(intent.desired_state, projection, capability.lossy_fields)
```

Never translate a native query silently. Every lossy or unsupported field is a
structured finding, and the planner returns `REVIEW`/`INCONCLUSIVE` when the
intent cannot be proven equivalent.

### Pattern 5: Governed mutation gate

```python
def authorize_apply(plan: ApplyPlan, policy: Policy, approval: ApprovalGate | None) -> None:
    if not policy.allows(plan.environment, plan.capability, mutation=True):
        raise ContractError("AF-OBS-POLICY", "mutation is not allowed by policy")
    if approval is None or approval.status != "approved":
        raise ContractError("AF-OBS-APPROVAL", "approved gate is required")
    if not plan.dry_run_digest or not plan.rollback_ref:
        raise ContractError("AF-OBS-GATE", "dry-run and rollback evidence are required")
```

The actual adapter call belongs after this gate and must emit a receipt with
credential reference, actor, capability, target, request hash, response hash,
verification result and rollback reference.

### Pattern 6: Deterministic performance validity

```python
def performance_verdict(run: PerformanceRun) -> Verdict:
    if run.environment is None or run.commit_sha is None:
        return Verdict.inconclusive("run identity is incomplete")
    if run.generator_saturated or run.downstream_unobserved:
        return Verdict.inconclusive("measurement validity conditions are unmet")
    return Verdict.pass_() if run.p99_ms <= run.target_p99_ms else Verdict.fail()
```

Reuse existing capacity/performance semantics: received requests are not
completed TPS, baselines must be preserved and generator saturation invalidates
a strong claim.

### Pattern 7: Declarative policy

```yaml
default_policy: local-ci-safe
policies:
  local-ci-safe:
    allow_observe: true
    allow_plan: true
    allow_apply: false
    allowed_environments: [local, ci]
    redact_attributes: true
    max_cardinality: 100
    require_approval_for: [monitor, slo, dashboard, event, deployment_marker]
    max_vendor_calls: 20
    timeout_seconds: 30
```

Configuration is data, versioned and hash-bound to a run. Environment-specific
policies can widen capabilities only through explicit approval and never through
agent output.

---

## Data Flow

```text
1. Discovery reads local/CI manifests, source trees, OpenAPI, runtime events
   and optional vendor/AWS/K8s/VM exports.
   │
   ▼
2. Source adapters validate input, hash it, redact attributes and emit source
   provenance plus canonical telemetry records.
   │
   ▼
3. Normalizer stores an immutable observation snapshot and graphify edges;
   missing, lossy and unsupported fields remain explicit.
   │
   ▼
4. Signal engine calculates RED/USE, percentiles, observed TPS, SLO,
   error-budget, burn-rate, cardinality, cost and drift findings.
   │
   ▼
5. Runtime supervisor creates TaskSpec-bound specialist invocations. Specialists
   produce evidence-bound findings and intents; disagreement opens a debate.
   │
   ▼
6. Critic attacks evidence, capabilities, cardinality, security and vendor
   projection. Referee resolves only when evidence supports a decision.
   │
   ▼
7. Planner projects intents into vendor-specific plans and stable diffs. Dry-run
   output is hashed and presented for review.
   │
   ▼
8. Governance gate validates policy, approval, credential reference and rollback.
   Apply is optional and isolated from the analysis path.
   │
   ▼
9. Verify compares observed state with desired state, writes receipts and emits
   DONE/REVIEW/BLOCKED with evidence and unresolved gaps.
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| OpenTelemetry/OTLP | JSON/OTLP ingest and optional export | None for offline fixtures; endpoint/token reference for live exporter |
| Datadog | Optional REST/API adapter for observe, plan and governed apply | API/app key reference or broker-issued short-lived credential; never persisted in core |
| Dynatrace | Optional environment/platform API adapter for observe, plan and governed apply | Token reference or broker-issued short-lived credential with declared scopes |
| AWS CloudWatch/X-Ray | Existing dump ingestion; optional read-only collector boundary | AWS role/profile reference outside core |
| AWS Secrets Manager/SSM | Credential broker integration | IAM role reference; no secret value in TaskSpec or telemetry |
| Kubernetes | Read-only discovery and optional apply adapter | Service account/identity reference outside core |
| VM/host | Read-only metadata/agent export | Host identity reference; no SSH secret in core |
| Terraform | Plan/desired-state analysis and diff | Local process/IaC artifact; apply remains separately gated |
| Graphify | Derived provenance/impact edges | Local canonical graph store |
| Runtime Agentico | Internal protocol/event integration | TaskSpec-bound local runtime policy |

Official design references: [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/general/trace/), [Dynatrace OpenTelemetry](https://docs.dynatrace.com/docs/ingest-from/opentelemetry), [Dynatrace SLOs](https://docs.dynatrace.com/docs/deliver/service-level-objectives), [Dynatrace SLO API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/service-level-objectives-classic) and [Datadog monitor-based SLOs](https://docs.datadoghq.com/service_level_objectives/monitor/).

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Contract/unit | Pydantic contracts, registry, provenance, redaction and cardinality | `tests/observability/test_contracts.py`, `test_redaction.py` | pytest, Pydantic schemas | 100% of required fields and refusal rules |
| Normalization | OTel/runtime/Datadog/Dynatrace/AWS/K8s/VM fixtures | `test_normalize.py`, `tests/fixtures/observability/` | pytest, JSON/YAML | ≥99% valid canonical fields; all invalid cases named |
| Signal/SLO | Percentiles, RED/USE, TPS validity, SLO, burn rate, missing data | `test_signals.py`, `test_slo.py` | pytest | Every success criterion SC-003 and AT-006/007 |
| Capability/projection | Vendor capability matrix, lossy fields, monitor/SLO/dashboard/event plans | `test_capabilities.py`, `test_intents.py` | pytest, fake adapters | No silent vendor equivalence |
| Governance/security | Redaction, secrets, allowlists, dry-run, approval, broker refs, apply, verify, rollback | `test_governance.py`, `test_redaction.py` | pytest, fake broker/server | 100% mutation paths gated |
| Drift/provenance | Snapshot hashes, desired/observed state, graph edges, receipts | `test_drift.py` | pytest | Reproducible diff and lineage |
| Agentic | Routing, dynamic fan-out, debate, critic, referee and final statuses | `test_runtime_instrumentation.py`, `test_vertical_slice.py` | pytest, FakeModelAdapter | At least 12 structural evals; no false DONE |
| Interface | CLI/MCP parity and detail levels | `test_interfaces.py` | Typer CliRunner, MCP registry | Every observability verb has matching projection |
| Evals | Routing, evidence, refusal, vendor asymmetry, SLO and hallucination resistance | `tests/evals/test_observability_evals.py`, YAML cases | pytest, structural evals | 8+ required scenarios, 12 target cases |
| Release | Contract docs, agent mirrors, no forbidden SDK imports, fixtures and catalog parity | `scripts/check_release.py` | release gate, Ruff, mypy | PASS required before build completion |

The first vertical slice is offline: synthetic OTel input → canonical snapshot
→ RED/SLO analysis → Datadog/Dynatrace intents → stable diff → blocked apply
without approval → REVIEW brief. Optional live integration tests are skipped
unless explicitly enabled and must never run in ordinary CI.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Invalid source schema | Return structured `AF-OBS-SCHEMA` diagnostic with source/path/hash; do not normalize partial data silently | No |
| Unknown/unsupported capability | Return `AF-OBS-CAPABILITY` and `INCONCLUSIVE`/`REVIEW` with vendor limitation | No |
| Redaction or policy violation | Block persistence/export/apply with `AF-OBS-REDACTION` or `AF-OBS-POLICY` | No |
| Rate limit / 429 | Preserve vendor response metadata, bounded exponential backoff with jitter under policy | Yes, bounded |
| Timeout/network failure | Return adapter receipt with target, attempt count and unresolved state | Yes, bounded |
| Credential reference missing/expired | Block before vendor call with `AF-OBS-CREDENTIAL` | No until approval/broker refresh |
| Missing SLO/performance evidence | Return `INCONCLUSIVE`, never infer values | No |
| Drift detected | Produce finding and diff; do not auto-apply | No |
| Approval missing/expired | Return `BLOCKED`/`REVIEW` and persist gate evidence | No |
| Apply response schema invalid | Mark operation failed, preserve request/response hashes and invoke rollback plan only if separately authorized | No automatic retry |
| Verification mismatch | Return `REVIEW`, receipt and rollback recommendation | Only via governed rollback |
| Agent disagreement | Open debate; critic/referee or human gate before final decision | No silent resolution |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `observability.policy_id` | string | `local-ci-safe` | Policy controlling observation, plan and mutation. |
| `observability.sources` | list[string] | `[otel-json, runtime]` | Enabled source adapters. |
| `observability.vendors` | list[string] | `[datadog, dynatrace]` | Vendor adapters to inspect/project. |
| `observability.allowed_environments` | list[string] | `[local, ci]` | Environments visible to the run. |
| `observability.allow_apply` | bool | `false` | Whether any external apply can be considered. |
| `observability.require_approval` | bool | `true` | Requires an ApprovalGate for all mutation intents. |
| `observability.redact_sensitive` | bool | `true` | Enforce attribute allowlist and secret/PII redaction. |
| `observability.max_cardinality` | int | `100` | Maximum dimension cardinality before a finding. |
| `observability.max_vendor_calls` | int | `20` | Bounded calls per TaskSpec-bound run. |
| `observability.timeout_seconds` | int | `30` | Per adapter call timeout. |
| `observability.max_retries` | int | `2` | Bounded retry count for transient vendor errors. |
| `observability.retention_days` | int | `7` | Local snapshot/replay retention subject to policy. |
| `observability.broker` | string/null | `null` | Credential broker reference; value is never a secret. |
| `observability.fixture_mode` | bool | `true` | Use fake/replay adapters in local/CI. |

Configuration is YAML, schema-validated, content-hashed into the run and
layered as defaults → environment → TaskSpec policy. Environment variables may
select a non-secret reference but may not carry raw vendor tokens into the
canonical runtime contracts.

---

## Security Considerations

- Keep vendor SDKs and HTTP clients behind optional adapter packages; the core
  must not import Datadog, Dynatrace or cloud SDKs.
- Store only credential references, scopes, actor, TTL and broker receipt; never
  secret values in TaskSpec, snapshots, events, graph edges, prompts or replay.
- Apply redaction before persistence, hashing, agent context, graph projection
  and vendor export. Deny headers, tokens, bodies, query values and user IDs by
  default.
- Treat vendor exports as untrusted input: validate schemas, bound payload size,
  reject unknown capability actions and preserve source hashes.
- Enforce least privilege, environment allowlists, capability allowlists,
  short-lived credentials, approval identity and separation of planner/apply.
- Make dry-run and diff mandatory for mutations. Verify the resulting state and
  keep a rollback reference; never treat a model response as authorization.
- Bound agent calls, concurrency, retries, timeouts, output size, cardinality
  and retention to limit cost and excessive agency.
- Do not expose raw DQL, Datadog queries, monitor IDs or resource metadata to
  agents unless redacted and required by the current TaskSpec.
- Security findings, unsupported mappings and missing evidence must lead to
  `REVIEW`, `BLOCKED` or `INCONCLUSIVE`, not optimistic completion.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured JSON events with run/task/revision/source/adapter/vendor/capability IDs; redaction before write. |
| Metrics | Counts and latency for ingest, normalize, analyze, plan, vendor calls, retries, rate limits, cardinality, SLO status, drift and apply/verify outcomes. |
| Tracing | OTel spans for each control-plane phase and adapter call; parent links to Runtime Agentico invocation and source trace/span when valid. |
| SLOs | Canonical SLI/SLO/error-budget/burn-rate contracts projected to Datadog and Dynatrace capabilities. |
| Audit | Append-only trajectory, policy hash, credential reference, approval, request/response hashes, receipt, verification and rollback evidence. |
| Cost | Token/economy ledger for agents plus vendor call count, payload bytes, cardinality and retention estimates. |
| Privacy | Redaction counters and blocked-field diagnostics; never log redacted values. |
| Debugging | Replay bundle contains sanitized source hash, policy, canonical snapshots, intents, diffs and deterministic fake responses. |

The control plane itself is the first observed workload. Vendor exporters are
optional; local CI always has enough structured evidence to diagnose behavior.

---

## Pipeline Architecture (if applicable)

### DAG Diagram

```text
[Sources]
   │
   ▼
[Validate + hash + redact]
   │
   ▼
[Canonical telemetry snapshot] ──→ [Graphify provenance]
   │
   ├──→ [RED/USE + SLO + cardinality + drift]
   │                         │
   │                         ▼
   └────────────────────→ [Agent intents + debate + critic]
                              │
                              ▼
                    [Vendor projection + diff]
                              │
                    [Dry-run / approval gate]
                              │
                    [Apply / verify / rollback]
```

### Partition Strategy

| Table/Store | Partition Key | Granularity | Rationale |
|-------------|---------------|-------------|-----------|
| Observation snapshots | `environment/service/observed_at` | Run/window | Isolate environments and bound replay/query cost. |
| Canonical spans/logs | `run_id/service_name/time_bucket` | Configurable time bucket | Preserve traceability without unbounded files. |
| Metric aggregates | `service/operation/window` | SLO window | Efficient RED/USE and SLO calculations. |
| Desired-state plans | `vendor/environment/intent_id` | Versioned plan | Stable diff and approval identity. |
| Receipts/audit | `task_id/run_id` | Append-only run | TaskSpec and runtime governance alignment. |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Source normalization | Content-hash cache | `source_sha256` | Reprocess only changed input |
| SLO aggregates | Windowed incremental | `observed_at` + service | Policy-defined SLO window |
| Vendor snapshots | Cursor/page checkpoint | Vendor cursor/reference | Adapter-defined, bounded |
| Drift state | Snapshot-to-snapshot | `snapshot_digest` | Previous accepted snapshot |
| Agent evals | Fixture case identity | `case_id` + version | Full case replay |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| New canonical field | Add optional field and versioned projection; require provenance when promoted | Read previous contract and mark field absent |
| Vendor field change | Adapter capability version and diagnostic; do not change canonical meaning silently | Pin adapter/schema version |
| SLO/intent semantics change | New intent/contract revision and migration projection | Revert to prior desired-state digest |
| Sensitive field discovered | Add deny rule and redact existing replay on next compaction | Keep only hash/diagnostic, never restore raw value |
| Removal/deprecation | Announce capability deprecation and preserve old reader | Use previous adapter while plan is unresolved |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|------------------|
| Contract validity | Pydantic + registry | 100% required fields valid | Block normalization |
| Source completeness | Normalizer diagnostics | ≥99% valid records or explicit gaps | REVIEW/INCONCLUSIVE |
| Redaction | Security tests | 0 secrets/forbidden payloads | Block persistence/export |
| Cardinality | Cardinality engine | ≤ configured budget | Finding and normalization recommendation |
| SLO validity | SLO engine | Identity, window and sample evidence present | INCONCLUSIVE |
| Vendor capability | Adapter matrix | No unsupported field silently projected | Block plan or mark lossy |
| Desired-state drift | Stable diff | Every change has owner/risk/evidence | REVIEW before apply |
| Apply verification | Receipt verifier | Observed state matches expected projection | REVIEW/rollback gate |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | design-agent | Initial technical design from DEFINE; control plane, contracts, adapters, agent team, governance and test manifest. |
| 1.1 | 2026-09-22 | ship-agent | Shipped and archived after build verification. |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_OBSERVABILITY_CONTROL_PLANE/`
