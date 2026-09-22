# DESIGN: API Forge gRPC Contract Control Plane

> Technical design for implementing the provider-neutral gRPC contract, compatibility, codegen and gateway control plane.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_GRPC_CONTRACT_CONTROL_PLANE |
| **Date** | 2026-09-22 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_GRPC_CONTRACT_CONTROL_PLANE.md](./DEFINE_API_FORGE_GRPC_CONTRACT_CONTROL_PLANE.md) |
| **Status** | ✅ Shipped |
| **Design Confidence** | 0.92 |

Confidence is high for the IR, compatibility and agentic boundaries because the
repository already has a protobuf extractor, versioned contracts, TaskSpec,
verification and observability control plane. Confidence is 0.80 for real
codegen and gateway execution because no live toolchains or services are
available; these paths are capability-gated and fixture-tested first.

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       API FORGE gRPC CONTROL PLANE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Inputs                                                                      │
│ [.proto] [FileDescriptorSet] [generated manifests] [runtime reports]       │
│ [OpenAPI/HTTP annotations] [OTel fixtures] [TaskSpec intention]            │
│                                      │                                      │
│                                      ▼                                      │
│ parser + descriptor loader → canonical gRPC IR + provenance + hashes       │
│                                      │                                      │
│                                      ▼                                      │
│ compatibility rules → compatible / review / breaking / inconclusive       │
│                                      │                                      │
│                                      ▼                                      │
│ TaskSpec planner → capability discovery → bounded specialist fan-out       │
│          │                    │                    │                       │
│          ▼                    ▼                    ▼                       │
│   codegen Python/Go/Java  gateway projections     runtime policies          │
│   protoc/Buf adapters      Envoy/Gateway/Web       deadlines/retry/health    │
│                                      │                                      │
│                                      ▼                                      │
│ contract/integration/stream/perf/security/OTel tests + evals               │
│                                      │                                      │
│                                      ▼                                      │
│ reviewer → verifier → holdout/mutation → receipts → DONE/REVIEW/BLOCKED   │
└─────────────────────────────────────────────────────────────────────────────┘
```

The canonical IR and analysis layers have no imports from `grpcio`, Go, Java,
Buf, Envoy, gRPC-Gateway, cloud SDKs or credentials. Adapters implement
protocols and return capability-aware results. Codegen and gateway operations
are local reversible artifacts by default; external mutation is a separate
brokered operation requiring policy, approval, diff and rollback evidence.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Proto source adapter | Extend existing textual extractor without breaking `proto.*` facts | Pure Python, existing `CodeInventory` |
| Descriptor adapter | Load `FileDescriptorSet` and preserve source provenance | Optional protobuf runtime/plugin |
| gRPC IR | Versioned representation of packages, services, RPCs, messages, fields, enums, options and streaming | Pydantic v2 frozen contracts |
| Compatibility engine | Compare baseline/candidate IR with explicit rules and evidence | Deterministic Python rules/catalog |
| Capability registry | Detect parser, protoc, Buf, language plugins, Envoy and gateway support | Protocols + YAML policy |
| Codegen adapters | Generate and verify Python, Go and Java clients/servers/stubs/manifests | protoc/Buf adapters, fake adapter |
| Gateway projections | Project HTTP annotations to gRPC-Gateway, Envoy, gRPC-Web and OpenAPI | Descriptor/config renderers |
| Runtime policy engine | Model deadlines, retries, status, metadata, health, reflection, interceptors, keepalive and shutdown | Declarative YAML + contracts |
| Streaming test engine | Validate four stream modes, cancellation, flow control and message limits | Fixtures, fake transport, optional runtime adapters |
| Performance analyzer | Separate RPS/TPS, concurrency, latency, stream throughput and generator saturation | Existing performance contracts + gRPC run contract |
| OTel bridge | Map RPC signals into Observability Control Plane contracts | Existing OTel/observability adapters |
| Agentic supervisor | Compile intention to TaskSpec, route specialists, debate critical divergence and verify | Runtime Agentico 2.0 |
| Evidence store | Persist IR, diffs, manifests, generated hashes, receipts and replay inputs | `.apiforge/grpc/`, graphify, TokenSave |
| CLI/MCP | Expose discover, analyze, diff, codegen, gateway, test, benchmark and verify | Typer + MCP parity |

---

## Key Decisions

### Decision 1: Canonical gRPC IR before codegen or gateway

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The repository must support multiple languages and gateways while
keeping compatibility decisions independent of installed toolchains.

**Choice:** Normalize `.proto` and descriptor inputs into `GrpcIR/v1` with
stable IDs, source refs, field numbers, wire types, streaming mode, options,
reserved declarations and unresolved diagnostics.

**Rationale:** The IR is the smallest stable boundary between source parsing,
compatibility, codegen, gateway projection, tests and agents. It also allows
the existing extractor to remain backward compatible.

**Alternatives Rejected:**

1. Runtime-first analysis — duplicates semantics across Python, Go and Java.
2. Gateway-first analysis — misses message/field evolution and generated-code risk.

**Consequences:** A richer contract must be versioned and documented; adapters
may report unsupported features rather than silently guessing.

### Decision 2: Descriptor sets enrich but do not replace source provenance

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Text parsing is useful offline, while descriptors contain resolved
types and options. Neither source alone should erase the other.

**Choice:** Accept `.proto` as the primary source and optional descriptor sets
as an enrichment artifact. Every IR node retains source path, line when known,
descriptor digest and unresolved imports/options.

**Rationale:** This supports local fixtures and real Buf/protoc pipelines while
keeping evidence traceable.

**Alternatives Rejected:** Descriptor-only ingestion because it loses readable
source context; parser-only because it cannot reliably resolve all imports and
custom options.

### Decision 3: Capability-aware projections instead of mandatory toolchains

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The user requires Python, Go, Java, gRPC-Gateway, Envoy and
gRPC-Web, but the local/CI environment may not contain every compiler/plugin.

**Choice:** Each adapter declares capabilities, versions, inputs, outputs and
whether it is read-only, local-reversible or externally mutating.

**Rationale:** The control plane remains useful without false success. Missing
toolchains yield `unsupported`/`BLOCKED` with an unlock path.

**Alternatives Rejected:** Hard dependencies on all toolchains; automatic
installation during agent execution; treating generated output as verified when
the compiler did not run.

### Decision 4: Compatibility policy is data, not scattered conditionals

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Field numbers, reserved ranges, enum values, presence, wire types,
RPC streaming and HTTP annotations have different compatibility semantics.

**Choice:** Store versioned compatibility rules and severity mappings in YAML;
the engine emits findings with rule IDs, evidence paths and confidence.

**Rationale:** Rules can evolve, be audited, tested independently and reused by
agents without changing the evaluator.

**Alternatives Rejected:** One generic breaking-change heuristic; model-only
classification without deterministic evidence.

### Decision 5: Generated artifacts are content-addressed evidence

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Codegen and gateway output must be reproducible across languages
and toolchain versions.

**Choice:** Store toolchain manifest, command intent, input digests, output
digests, diagnostics and reproducibility result; never infer output equality
from filenames alone.

**Rationale:** This supports replay, holdout, mutation checks and independent
verification.

### Decision 6: Runtime and performance claims remain evidence-bound

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** gRPC streaming, flow control and generator saturation can make an
apparently good benchmark invalid.

**Choice:** Preserve missing metrics, distinguish RPS from business TPS, record
generator/resource saturation and return `inconclusive` where validity is not
proven.

**Alternatives Rejected:** Filling missing values with zero; declaring capacity
from a single run; treating client-side throughput as server capacity.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/grpc.py` | Create | Versioned gRPC IR, RPC mode, descriptor, compatibility, codegen, gateway, runtime and evidence contracts | @api-grpc-contract-engineer | existing contracts/base.py |
| 2 | `src/apiforge/contracts/registry.py` | Modify | Register gRPC contracts | @api-grpc-contract-engineer | 1 |
| 3 | `docs/contracts/GrpcIR-v1.md` | Create | Document canonical IR invariants | @api-dx-docs-reviewer | 1 |
| 4 | `docs/contracts/GrpcCompatibility-v1.md` | Create | Document diff classifications and evidence | @api-dx-docs-reviewer | 1 |
| 5 | `docs/contracts/GrpcCodegen-v1.md` | Create | Document generated artifact manifest and reproducibility | @api-dx-docs-reviewer | 1 |
| 6 | `docs/contracts/GrpcGateway-v1.md` | Create | Document gateway capability/projection semantics | @api-dx-docs-reviewer | 1 |
| 7 | `src/apiforge/grpc/__init__.py` | Create | Public gRPC control-plane API | @api-grpc-contract-engineer | 1, 8 |
| 8 | `src/apiforge/grpc/ir.py` | Create | Build canonical IR from facts/descriptors | @api-grpc-contract-engineer | 1, 9, 10 |
| 9 | `src/apiforge/adapters/protobuf/extract.py` | Modify | Preserve legacy facts and expose richer syntax/source refs | @api-grpc-parser-engineer | existing protobuf tests |
| 10 | `src/apiforge/adapters/protobuf/descriptor.py` | Create | Load descriptor sets without mandatory runtime dependency | @api-grpc-parser-engineer | 1 |
| 11 | `src/apiforge/grpc/source.py` | Create | Source and descriptor input normalization | @api-grpc-parser-engineer | 8, 10 |
| 12 | `src/apiforge/grpc/compatibility.py` | Create | Deterministic baseline/candidate diff engine | @api-grpc-compatibility-engineer | 1, 8, 13 |
| 13 | `src/apiforge/rules/grpc_compatibility.yaml` | Create | Compatibility rules and severity mappings | @api-grpc-compatibility-engineer | 1 |
| 14 | `src/apiforge/grpc/capabilities.py` | Create | Toolchain/plugin/gateway capability registry | @api-grpc-toolchain-engineer | 1 |
| 15 | `src/apiforge/grpc/codegen.py` | Create | Deterministic codegen planner and manifest builder | @api-grpc-codegen-engineer | 1, 14 |
| 16 | `src/apiforge/grpc/codegen_adapters.py` | Create | Fake, protoc/Buf, Python, Go and Java adapters | @api-grpc-codegen-engineer | 14, 15 |
| 17 | `src/apiforge/grpc/artifacts.py` | Create | Hash generated outputs and verify reproducibility | @api-verification-engineer | 15, 16 |
| 18 | `src/apiforge/grpc/gateway.py` | Create | Gateway projection planner and capability results | @api-grpc-gateway-engineer | 1, 14 |
| 19 | `src/apiforge/grpc/gateway_adapters.py` | Create | Envoy, gRPC-Gateway, gRPC-Web and OpenAPI projections | @api-grpc-gateway-engineer | 18 |
| 20 | `src/apiforge/grpc/runtime_policy.py` | Create | Deadline/retry/status/metadata/health/reflection policy | @api-grpc-runtime-engineer | 1, 21 |
| 21 | `src/apiforge/rules/grpc_runtime.yaml` | Create | Runtime policy defaults and risk mappings | @api-grpc-runtime-engineer | 20 |
| 22 | `src/apiforge/grpc/streaming.py` | Create | Streaming mode, cancellation, flow-control and limits analysis | @api-grpc-runtime-engineer | 1, 20 |
| 23 | `src/apiforge/grpc/performance.py` | Create | gRPC run validity, TPS/RPS and stream throughput | @api-grpc-performance-engineer | 22, existing perf |
| 24 | `src/apiforge/grpc/observability.py` | Create | Map RPC telemetry to OTel control plane | @api-grpc-observability-engineer | existing observability |
| 25 | `src/apiforge/grpc/security.py` | Create | mTLS/auth metadata, secret redaction and mutation gates | @api-grpc-security-engineer | 20, existing policy |
| 26 | `src/apiforge/grpc/plan.py` | Create | Compile gRPC intention into TaskSpec and proof axes | @api-agentic-orchestrator | 12, 15, 18, 25 |
| 27 | `src/apiforge/grpc/verify.py` | Create | Independent verification, holdout and mutation checks | @api-verification-engineer | 17, 19, 23, 26 |
| 28 | `src/apiforge/graph/build.py` | Modify | Add gRPC IR/diff/codegen/gateway provenance edges | @api-grpc-contract-engineer | 8, 12, 17 |
| 29 | `src/apiforge/brief/render.py` | Modify | Render gRPC outcomes and unresolved capabilities | @api-release-guardian | 27 |
| 30 | `src/apiforge/cli.py` | Modify | Add `grpc discover|analyze|diff|codegen|gateway|test|benchmark|verify` | @api-grpc-agentic-engineer | 26, 27 |
| 31 | `src/apiforge/mcp/tools.py` | Modify | CLI/MCP parity for gRPC operations | @api-grpc-agentic-engineer | 30 |
| 32 | `src/apiforge/rules/playbooks.yaml` | Modify | gRPC specialist playbooks | @api-agentic-orchestrator | 26, 30 |
| 33 | `src/apiforge/rules/routing.yaml` | Modify | Route gRPC phases and risk areas | @api-planner | 32 |
| 34 | `agents/api-grpc-contract-engineer.md` | Create | IR and contract specialist | @api-grpc-contract-engineer | 1, 8 |
| 35 | `agents/api-grpc-parser-engineer.md` | Create | `.proto` and descriptor specialist | @api-grpc-parser-engineer | 9, 10 |
| 36 | `agents/api-grpc-compatibility-engineer.md` | Create | Breaking-change and evolution specialist | @api-grpc-compatibility-engineer | 12, 13 |
| 37 | `agents/api-grpc-toolchain-engineer.md` | Create | protoc/Buf/plugin capability specialist | @api-grpc-toolchain-engineer | 14, 16 |
| 38 | `agents/api-grpc-codegen-engineer.md` | Create | Python/Go/Java generated artifact specialist | @api-grpc-codegen-engineer | 15, 16, 17 |
| 39 | `agents/api-grpc-gateway-engineer.md` | Create | Envoy/gRPC-Gateway/Web/OpenAPI specialist | @api-grpc-gateway-engineer | 18, 19 |
| 40 | `agents/api-grpc-runtime-engineer.md` | Create | Streaming/resilience/runtime specialist | @api-grpc-runtime-engineer | 20, 22 |
| 41 | `agents/api-grpc-performance-engineer.md` | Create | TPS, flow-control and stress specialist | @api-grpc-performance-engineer | 23 |
| 42 | `agents/api-grpc-observability-engineer.md` | Create | OTel RPC instrumentation specialist | @api-grpc-observability-engineer | 24 |
| 43 | `agents/api-grpc-security-engineer.md` | Create | mTLS/auth/metadata/safety specialist | @api-grpc-security-engineer | 25 |
| 44 | `agents/api-grpc-agentic-engineer.md` | Create | TaskSpec, routing, debate and supervisor specialist | @api-grpc-agentic-engineer | 26, 30, 31 |
| 45 | `tests/grpc/test_contracts.py` | Create | IR and contract validation | @api-test-strategist | 1, 2 |
| 46 | `tests/grpc/test_parser.py` | Create | Source/descriptor parsing and legacy parity | @api-grpc-parser-engineer | 9, 10 |
| 47 | `tests/grpc/test_compatibility.py` | Create | 20+ compatibility cases | @api-grpc-compatibility-engineer | 12, 13 |
| 48 | `tests/grpc/test_codegen.py` | Create | Fake and real-toolchain capability/codegen tests | @api-grpc-codegen-engineer | 15, 16, 17 |
| 49 | `tests/grpc/test_gateway.py` | Create | Envoy/Gateway/Web/OpenAPI projections | @api-grpc-gateway-engineer | 18, 19 |
| 50 | `tests/grpc/test_runtime_policy.py` | Create | Deadlines, retries, status, health and metadata | @api-grpc-runtime-engineer | 20, 21 |
| 51 | `tests/grpc/test_streaming.py` | Create | Four streaming modes and failure boundaries | @api-grpc-runtime-engineer | 22 |
| 52 | `tests/grpc/test_performance.py` | Create | TPS/RPS, latency, stream throughput and saturation | @api-grpc-performance-engineer | 23 |
| 53 | `tests/grpc/test_observability.py` | Create | OTel mapping and correlation | @api-grpc-observability-engineer | 24 |
| 54 | `tests/grpc/test_security.py` | Create | Credentials, redaction and mutation refusal | @api-grpc-security-engineer | 25 |
| 55 | `tests/grpc/test_agentic.py` | Create | TaskSpec, debate, reviewer and verifier gates | @api-grpc-agentic-engineer | 26, 27 |
| 56 | `tests/grpc/test_vertical_slice.py` | Create | Offline end-to-end gRPC control plane | @api-test-strategist | 8–27 |
| 57 | `tests/grpc/test_cli_mcp_parity.py` | Create | CLI/MCP payload parity | @api-dx-docs-reviewer | 30, 31 |
| 58 | `tests/evals/cases/grpc_cases.yaml` | Create | At least 20 structural and safety eval cases | @api-test-strategist | 45–57 |
| 59 | `tests/evals/test_grpc_evals.py` | Create | Evaluate routing, evidence, compatibility and safety | @api-test-strategist | 58 |
| 60 | `evals/skills/evals.json` | Modify | Register gRPC eval suite | @api-test-strategist | 58, 59 |
| 61 | `tests/fixtures/grpc/` | Create | Valid, invalid, evolution, streaming and gateway fixtures | @api-test-strategist | None |
| 62 | `src/apiforge/rules/grpc.yaml` | Create | Feature policy, thresholds and toolchain config | @api-grpc-contract-engineer | 1, 14 |
| 63 | `scripts/check_release.py` | Modify | Validate gRPC contracts, agents, fixtures and safety | @api-release-guardian | 1, 34–44 |
| 64 | `docs/catalog-contract.md` | Modify | Document gRPC error/capability codes | @api-dx-docs-reviewer | 12, 14, 27 |
| 65 | `.agents/agents/api-grpc-specialists.md` | Create | Host mirror bundle manifest | @api-release-guardian | 34–44 |
| 66 | `.claude/agents/api-grpc-specialists.md` | Create | Host mirror bundle manifest | @api-release-guardian | 34–44 |

**Total Files:** 66 primary manifest paths, plus derived per-profile mirrors for rows 34–44.

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @api-grpc-contract-engineer | 1, 7, 28, 62 | Owns canonical IR, graph provenance and contract boundaries. |
| @api-grpc-parser-engineer | 9–11, 46 | Matches protobuf extraction and descriptor ingestion. |
| @api-grpc-compatibility-engineer | 12, 13, 36, 47 | Owns evolution, breaking changes and evidence. |
| @api-grpc-toolchain-engineer | 14, 37 | Owns capability detection and toolchain unlocks. |
| @api-grpc-codegen-engineer | 15–17, 38, 48 | Owns reproducible Python/Go/Java artifacts. |
| @api-grpc-gateway-engineer | 18, 19, 39, 49 | Owns Envoy, gRPC-Gateway, Web and OpenAPI. |
| @api-grpc-runtime-engineer | 20–22, 40, 50, 51 | Owns streaming, deadlines and resilience. |
| @api-grpc-performance-engineer | 23, 41, 52 | Owns valid throughput and stress evidence. |
| @api-grpc-observability-engineer | 24, 42, 53 | Owns OTel RPC signals and correlation. |
| @api-grpc-security-engineer | 25, 43, 54 | Owns mTLS/auth/metadata and mutation safety. |
| @api-grpc-agentic-engineer | 26, 30, 31, 44, 55 | Owns TaskSpec, routing, debate and CLI/MCP. |
| @api-verification-engineer | 17, 27 | Independently checks generated artifacts and proof axes. |
| @api-test-strategist | 45, 56, 58–61 | Owns deterministic fixtures, vertical testing and eval quality gates. |
| @api-release-guardian | 29, 63, 65, 66 | Owns release integrity and mirror drift. |
| @api-dx-docs-reviewer | 3–6, 57, 64 | Owns public contract and CLI/MCP documentation. |

**Agent Discovery:** Scanned `agents/**/*.md`; existing profiles cover runtime,
performance, security, testing, observability, planning, verification and
release. Eleven gRPC-specific profiles are new design artifacts and must be
mirrored under `.agents/agents/` and `.claude/agents/` by the release step.

---

## Code Patterns

### Pattern 1: Frozen versioned IR with explicit stream mode

```python
from typing import Literal
from pydantic import Field
from apiforge.contracts.base import VersionedContract

RpcMode = Literal["unary", "client_streaming", "server_streaming", "bidi_streaming"]


class GrpcRpc(VersionedContract):
    service: str
    name: str
    request_type: str
    response_type: str
    mode: RpcMode
    source_path: str
    field_numbers: tuple[int, ...] = Field(default_factory=tuple)
    unresolved: tuple[str, ...] = Field(default_factory=tuple)
```

This follows the existing frozen/closed contract pattern and keeps absent
information explicit instead of defaulting it into a false fact.

### Pattern 2: Protocol-based adapter and capability result

```python
from pathlib import Path
from typing import Protocol


class GrpcToolAdapter(Protocol):
    name: str

    def available(self) -> bool: ...

    def generate(self, source: Path, output: Path, *, dry_run: bool) -> dict[str, object]: ...
```

The core depends on the protocol; fake, protoc, Buf, Envoy and language
adapters implement it. A missing binary returns a typed unsupported result.

### Pattern 3: Evidence-bound compatibility rule

```python
def classify_field_number_change(before: int | None, after: int | None) -> str:
    if before is None and after is not None:
        return "compatible"
    if before != after:
        return "breaking"
    return "unchanged"
```

The production implementation will attach rule ID, baseline/candidate paths,
source hashes and confidence to the classification; the snippet illustrates
the pure-function boundary.

### Pattern 4: Capability-aware codegen configuration

```yaml
toolchains:
  protoc:
    required: false
    command: protoc
  buf:
    required: false
    command: buf
targets:
  python: {enabled: true, plugin: grpc_python_plugin}
  go: {enabled: true, plugin: protoc-gen-go-grpc}
  java: {enabled: true, plugin: protoc-gen-grpc-java}
gateways:
  envoy: {enabled: true, descriptor_required: true}
  grpc_gateway: {enabled: true, annotations_required: true}
  grpc_web: {enabled: true}
policy:
  external_mutation: approval_and_broker
  missing_evidence: inconclusive
```

### Pattern 5: Agentic plan with independent verification

```python
def build_grpc_task(intent: dict[str, object]) -> dict[str, object]:
    return {
        "strategy": "verified-grpc-contract-slice",
        "proof_axes": ("ir", "compatibility", "generated_artifacts", "gateway", "tests"),
        "acceptance": ("no_unexplained_breaking_change", "reproducible_outputs"),
        "rollback": "discard sandbox artifacts and restore baseline digest",
        "external_mutation": False,
        "intent": intent,
    }
```

The supervisor dynamically fans out only independent tasks, invokes debate on
high-risk/divergent decisions, and never lets the originating agent certify its
own final proof.

---

## Data Flow

```text
1. User intention or .proto/descriptor input
   │
   ▼
2. Source adapter parses files and records diagnostics/hashes
   │
   ▼
3. Normalizer builds GrpcIR/v1 and graph provenance
   │
   ▼
4. Compatibility engine compares baseline/candidate with YAML rules
   │
   ▼
5. Capability registry selects fake/protoc/Buf/language/gateway adapters
   │
   ▼
6. TaskSpec planner creates independent codegen, gateway, test and perf tasks
   │
   ▼
7. Sandbox executes local artifacts; OTel/perf adapters collect evidence
   │
   ▼
8. Reviewer, verifier, holdout and mutation checks produce receipts
   │
   ▼
9. CLI/MCP renders DONE, REVIEW, INCONCLUSIVE or BLOCKED
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| `protoc` | Local subprocess adapter | None; binary capability check |
| Buf | Local subprocess/config adapter | None; binary capability check |
| Python `grpcio` | Optional runtime/codegen adapter | Local environment only |
| Go `grpc-go` | Optional codegen/runtime fixture adapter | Local toolchain only |
| Java `grpc-java` | Optional codegen/runtime fixture adapter | Local toolchain only |
| Envoy | Descriptor/config projection | None in core; deployment broker later |
| gRPC-Gateway | Generated proxy projection | None in core; deployment broker later |
| gRPC-Web | Generated/client and proxy projection | None in core; deployment broker later |
| OpenTelemetry | Existing observability adapter | Local fixture or approved collector |
| AWS ECS/EKS/Lambda/EC2/MSK | Read-only manifests/dumps initially | AWS adapter outside core |
| Datadog/Dynatrace | Existing observability vendor boundary | Credential broker only for mutation |

Official constraints reflected in the design include explicit gRPC deadlines,
health service, status/trailers and streaming semantics; Envoy transcoding
requires descriptors and HTTP annotations; gRPC-Gateway introduces JSON ↔
protobuf conversion and generated proxy maintenance.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | IR, parser, rules, stream modes, policy | `tests/grpc/test_contracts.py`, `test_parser.py`, `test_compatibility.py`, `test_runtime_policy.py` | pytest, parametrize | All 28 acceptance IDs mapped |
| Contract | Versioned schemas and registry | `tests/grpc/test_contracts.py` | Pydantic + pytest | 100% required fields and closed enums |
| Codegen | Fake plus optional real toolchains | `tests/grpc/test_codegen.py` | pytest, subprocess capability mocks | Byte-reproducibility and unsupported states |
| Gateway | Envoy/Gateway/Web/OpenAPI projections | `tests/grpc/test_gateway.py` | pytest, descriptor fixtures | 8+ projection cases |
| Streaming | Unary/client/server/bidi, cancel, flow and limits | `tests/grpc/test_streaming.py` | fake transport, pytest | All four modes and failure edges |
| Integration | IR → diff → codegen → gateway → evidence | `tests/grpc/test_vertical_slice.py` | pytest, temp sandbox | Full offline path |
| Performance | RPS/TPS, p99, concurrency, stream throughput | `tests/grpc/test_performance.py` | existing perf contracts | Invalid/saturated runs become inconclusive |
| Security | mTLS/auth metadata/redaction/mutation | `tests/grpc/test_security.py` | pytest, fake broker | Zero secret leakage and zero unauthorized mutation |
| Agentic/eval | Routing, debate, reviewer, holdout, mutation | `tests/grpc/test_agentic.py`, `tests/evals/test_grpc_evals.py` | pytest, declarative YAML | ≥20 eval cases; no false DONE |
| CLI/MCP | Payload and error parity | `tests/grpc/test_cli_mcp_parity.py` | Typer runner + MCP fakes | Semantic parity for every public verb |
| Full regression | Existing API Forge behavior | existing suite | Ruff, mypy, pytest, release gate | No regression |

Every DEFINE acceptance test maps directly to one or more manifest test files;
AT-023–AT-027 are critical gates and require independent verification.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Invalid `.proto` / descriptor | Emit typed diagnostic with source/hash; preserve partial facts only when safe | No |
| Missing import | Mark unresolved and block only operations needing resolution | No automatic retry |
| Missing toolchain/plugin | Return capability `unsupported` with unlock instructions | No |
| Codegen non-reproducible | Fail artifact verification and produce REVIEW | No |
| Breaking compatibility | Produce finding and block `DONE`; approval/debate required for plan | No |
| Deadline exceeded | Preserve `DEADLINE_EXCEEDED`, cancellation and evidence | Retry only if policy/idempotency allows |
| Retry on non-idempotent RPC | Refuse automatic retry | No |
| Stream cancellation/backpressure | Close resources, record status and classify run limitation | Bounded policy only |
| Gateway projection mismatch | Reject projection and cite descriptor/annotation difference | No |
| External mutation without approval/broker | Refuse before adapter call | No |
| Tool subprocess failure | Capture exit code/stdout/stderr digest; return REVIEW/BLOCKED | Bounded retry only for deterministic transient setup |
| Missing performance metric | Preserve `None`, label inconclusive | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `grpc.source_mode` | string | `proto_or_descriptor` | Allowed source inputs |
| `grpc.compatibility_policy` | string | `strict-evidence` | Rule set for breaking classification |
| `grpc.toolchain.protoc` | string | `protoc` | Optional executable name/path |
| `grpc.toolchain.buf` | string | `buf` | Optional executable name/path |
| `grpc.targets.python.enabled` | bool | `true` | Enable Python codegen target |
| `grpc.targets.go.enabled` | bool | `true` | Enable Go codegen target |
| `grpc.targets.java.enabled` | bool | `true` | Enable Java codegen target |
| `grpc.gateway.envoy.enabled` | bool | `true` | Enable Envoy projection |
| `grpc.gateway.grpc_gateway.enabled` | bool | `true` | Enable gRPC-Gateway projection |
| `grpc.gateway.grpc_web.enabled` | bool | `true` | Enable gRPC-Web projection |
| `grpc.limits.max_message_bytes` | int | `4194304` | Declared message-size policy |
| `grpc.limits.max_stream_duration_s` | int | `3600` | Analysis/runtime stream bound |
| `grpc.performance.min_samples` | int | `100` | Minimum evidence for valid comparison |
| `grpc.performance.max_generator_saturation` | float | `0.8` | Above this, capacity result is inconclusive |
| `grpc.governance.external_mutation` | string | `approval_and_broker` | Required mutation boundary |

---

## Security Considerations

- Treat metadata, authorization headers, peer certificates and generated config as sensitive; redact before persistence and graph projection.
- Keep mTLS, OAuth/JWT/API-key and service-account values as credential references; the core never receives raw secrets.
- Validate authority/service/method names and descriptor imports against allowlists to prevent path traversal and dependency injection.
- Bound message size, stream duration, concurrent streams, metadata size and generated output size.
- Do not enable automatic retries for non-idempotent RPCs; require explicit idempotency evidence.
- Reflection is a controlled diagnostic capability, not a production authorization mechanism.
- Sandbox all subprocess codegen/gateway tools with timeout, output limits and no uncontrolled network access.
- External deployment/configuration requires dry-run, stable diff, human approval, broker, receipt and rollback plan.
- Preserve source hashes and provenance while excluding raw PII/secrets from fixtures and evidence.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured JSON events with task ID, run ID, service, fully-qualified RPC, stream mode, status and correlation ID; redaction before persistence. |
| Metrics | Parse duration, IR nodes, unresolved imports, breaking findings, codegen duration, artifact count, gateway projection count, RPC latency, message bytes, active streams, cancellations, retries and verifier outcomes. |
| Tracing | OTel spans for parse, normalize, diff, codegen, gateway projection, sandbox command, test case and verification; propagate `trace_id`/`task_id`. |
| SLO | Reuse Observability Control Plane for availability, deadline errors, p99, stream completion and error budget. |
| Cost/economy | TokenSave records input/output bytes, cached descriptor/parser stages, replay hits and model/tool calls. |
| Provenance | Graphify edges connect source → IR → finding → generated artifact → gateway projection → test/evidence → receipt. |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | design-agent | Initial design for gRPC IR, compatibility, codegen, gateways, streaming, performance and agentic verification. |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_GRPC_CONTRACT_CONTROL_PLANE/`

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.1 | 2026-09-22 | Shipped and archived. |
