# DESIGN: API Git CI/CD Change Control Plane

> Technical design for implementing the read-only API change and CI/CD governance control plane.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `API_GIT_CICD_CHANGE_CONTROL_PLANE` |
| **Date** | 2026-09-22 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_GIT_CICD_CHANGE_CONTROL_PLANE.md](./DEFINE_API_GIT_CICD_CHANGE_CONTROL_PLANE.md) |
| **Status** | ✅ Shipped |
| **Design Confidence** | 0.95 |

The confidence is high because the design extends existing typed contracts, gateway, case artifacts, evidence chain, CLI/MCP projections and agent catalog. The live GitHub transport, real anonymized samples and provider policy remain implementation proof obligations.

---

## Architecture Overview

```text
┌────────────────────────────────────────────────────────────────────┐
│                     API CHANGE CONTROL PLANE                       │
├────────────────────────────────────────────────────────────────────┤
│ PR / branch event                         Manual replay             │
│        │                                      │                    │
│        └──────────────┬───────────────────────┘                    │
│                       ▼                                            │
│             [Workflow ingress + policy]                            │
│                       │                                            │
│          ┌────────────┴────────────┐                               │
│          ▼                         ▼                               │
│ [GitHub read-only adapter]  [Artifact replay adapter]              │
│          │                         │                               │
│          └────────────┬────────────┘                               │
│                       ▼                                            │
│          [Normalized ChangeBundle/v1]                              │
│        source refs + hashes + limits                               │
│                       │                                            │
│                       ▼                                            │
│             [Change control application]                            │
│   case → analyze → next-step → graph → evidence → brief            │
│                       │                                            │
│          ┌────────────┼─────────────┐                              │
│          ▼            ▼             ▼                              │
│ [Agent evaluator] [Metrics] [Canonical CapabilityResult]           │
│          │            │             │                               │
│          └────────────┴─────────────┘                               │
│                       ▼                                            │
│        JSON / Markdown / JUnit / receipt artifacts                 │
│              CI artifact upload → IDE / UI / MCP                   │
└────────────────────────────────────────────────────────────────────┘
```

The external adapter is the only component allowed to perform read-only provider I/O. The application accepts a normalized bundle and can replay it without network. No component in this feature mutates GitHub, executes PR code, merges, pushes, deploys or changes a workflow.

### Layering

```text
contracts (pure schemas)
        ▲
application (use case, case/artifact orchestration)
        ▲
integrations (GitHub transport and artifact replay)
        ▲
surfaces/workflow (CLI, MCP, IDE/UI projections, GitHub Actions)
```

The dependency direction follows the Python clean-architecture KB: domain contracts do not import adapters; adapters implement explicit protocols; surfaces call the application use case instead of duplicating business rules.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `ChangeBundle/v1` contracts | Validate provider context, source references, diff, checks, artifacts, policy and replay metadata. | Pydantic v2 models, strict validators, canonical JSON |
| GitHub read-only adapter | Collect PR/branch metadata, base/head refs, diff, checks and artifact references through an injected read-only transport. | Python stdlib transport boundary; no provider SDK in core |
| Artifact replay adapter | Load a previously sanitized bundle, verify hashes and reconstruct the same normalized input without network. | Local filesystem, `core.io`, receipt/hash validation |
| Change control application | Create isolated case, invoke existing analyze/routing/graph/evidence/brief services, collect failures as governed results. | `src/apiforge/application/`, existing case artifacts |
| Recommendation evaluator | Validate `AgentArtifact/v1`, compare goldens/holdouts, report unsupported optimism and evaluation metrics. | Deterministic pytest/eval service, Pydantic validation |
| Evidence publisher | Write canonical JSON, Markdown, JUnit, metrics and receipt references under the run artifact directory. | Atomic JSON/JSONL files, existing receipt conventions |
| Capability gateway | Expose `api.change-control`, `git.read-context` and `cicd.inspect-run` through the existing gateway and surface projections. | `CapabilityRequest/Result`, policy gate |
| Workflow ingress | Pass event/manual inputs, select safe job path, install project and upload artifacts. | GitHub Actions YAML, least-privilege permissions |
| Route catalog extension | Route contract findings in `discover` as well as `verify`, without changing finding semantics. | YAML rules catalog + routing test |
| Agent evaluator/reviewer | Recommend API governance, verification, security and observability specialists based on facts and explicit unresolved items. | Existing project agents and supervisor |

---

## Key Decisions

### Decision 1: Normalize provider input before invoking the core

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** GitHub event payloads, checks and artifacts are external, mutable in shape and not suitable as direct inputs to the deterministic case pipeline. The same change must also be replayable locally without network.

**Choice:** Introduce a versioned `ChangeBundle/v1` with typed source references, content hashes, base/head identity, API contract inputs, CI observations, policy context and explicit limitations. The GitHub adapter and artifact replay adapter both produce this bundle; the application consumes only this bundle.

**Rationale:** This creates one stable boundary for PR, branch and manual execution, permits deterministic replay, preserves source provenance and prevents provider-specific semantics from leaking into `analyze`, `next-step`, graph or evidence code. Pydantic validation makes malformed payloads a named failure rather than a traceback.

**Alternatives Rejected:**

1. Passing raw GitHub JSON through the application — rejected because schemas, secrets and provider assumptions would be spread across the core.
2. Reading the live provider from `analyze` — rejected because local analysis must remain offline-first and replayable.

**Consequences:**

- A bundle schema and version migration policy must be maintained.
- Provider fields not mapped to the bundle remain explicit `unresolved` evidence.
- Local replay becomes a first-class verifier, not a convenience script.

---

### Decision 2: Use an injected transport and keep provider access read-only

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The first real external adapter is GitHub, but importing a provider SDK or embedding network assumptions in the core conflicts with the project boundary. Tests must be deterministic and must not require credentials.

**Choice:** Define a small `ReadOnlyTransport` protocol. The GitHub adapter builds fixed GET requests, validates response envelopes, redacts sensitive fields and returns `ChangeBundle/v1`. Production CI supplies an explicit transport implementation; tests supply an in-memory transport. There are no POST, PUT, PATCH or DELETE methods in this feature.

**Rationale:** Dependency inversion makes read-only behavior auditable, supports fixture-based tests and leaves a future provider adapter behind the same boundary. It also allows the local replay mode to avoid importing or calling a network implementation at all.

**Alternatives Rejected:**

1. A GitHub SDK imported in `src/` — rejected by project policy and makes credentials/versions part of the core.
2. Shelling out to `gh` from the application — rejected because it creates hidden authentication and process behavior that is harder to verify.

**Consequences:**

- The CI host must provide a transport and read-only token policy.
- HTTP status, pagination, rate limiting and missing permissions become typed adapter outcomes.
- The adapter proves only the fields returned by GitHub; runtime execution remains a separate evidence claim.

---

### Decision 3: Publish artifacts, not provider mutations

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The selected feature is read-only. A PR comment or status is a write operation even if it only contains a recommendation, and it would require a different permission and rollback policy.

**Choice:** Publish JSON, Markdown, JUnit, metrics and receipt files as CI artifacts. IDE, MCP and UI consume the canonical result or the downloaded bundle. Provider comments/status, merge and deployment remain separate future adapters.

**Rationale:** Artifacts are immutable inputs for later replay and do not require the API to mutate user-owned state. This meets auditability and local-first requirements with a smaller security surface.

**Alternatives Rejected:**

1. Automatic PR comments/status — rejected for the MVP because it expands permissions and creates external state to roll back.
2. Persistent control-plane service — rejected because the first proof does not require a database, webhook or service lifecycle.

**Consequences:**

- Reviewers need a CI artifact link or IDE/UI projection.
- A future write adapter must have its own capability, policy, approval, rollback and receipt.

---

### Decision 4: Governed terminal states instead of exception-driven control flow

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Missing tokens, malformed provider payloads, unavailable checks and routing gaps are expected boundary conditions. A traceback hides the distinction between invalid input, missing evidence and product failure.

**Choice:** Map expected failures to typed `ChangeControlError` records with `AF-*` codes, persisted diagnostics and terminal `ok`, `review`, `blocked` or `failed` results. Unexpected exceptions are caught only at the CLI/workflow boundary, logged with correlation identifiers and converted to a governed failure artifact.

**Rationale:** This preserves evidence and lets the verifier distinguish “the change is unsafe” from “the provider could not be observed”. It follows the KB error-handling pattern: catch specific errors at the handling boundary, chain causes, and never use a bare catch.

**Alternatives Rejected:**

1. Letting Typer expose raw tracebacks — rejected because critical flows must be safe for CI and human review.
2. Treating every adapter error as success with empty data — rejected because missing evidence must remain visible and unresolved.

**Consequences:**

- Error codes and recovery guidance become part of the public contract.
- The CI exit policy must be defined separately from capability state; `review` is not silently converted to success.

---

### Decision 5: Evaluate recommendations structurally and behaviorally with deterministic samples

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** A valid JSON recommendation can still be unsupported, overconfident or inconsistent with the evidence. The project requires agents to understand the need, recommend practices and architectures, and preserve uncertainty.

**Choice:** Validate the nine-field output contract first, then compare normalized recommendation facts against reviewed goldens and adversarial holdouts. Real anonymized samples are replayed as external-evidence cases. The evaluator records matches, omissions, unsupported claims and confidence without allowing evaluation to promote an unresolved fact to confirmed.

**Rationale:** The genai evaluation KB recommends structured output, explicit rubrics, ground truth and continuous quality checks. The project-specific adaptation is deterministic: no model is required for the core evaluator, and any model-based judge remains outside the core and advisory.

**Alternatives Rejected:**

1. Accepting recommendations based only on schema validity — rejected because syntax does not prove evidence grounding.
2. Making an LLM judge the release gate — rejected because model availability and judgment would violate offline determinism.

**Consequences:**

- Goldens need human review and holdouts must intentionally contain uncertainty.
- Evaluation output itself needs hashes and provenance.
- A failing evaluator produces `review`/`blocked` evidence, not a rewritten recommendation.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/change_control.py` | Create | `ChangeBundle/v1`, source, check, artifact, policy, recommendation and metrics contracts. | `@api-contract-architect` | Existing `contracts.base`, `core.models` |
| 2 | `src/apiforge/integrations/github.py` | Create | GitHub read-only adapter, request allowlist, response normalization and redaction boundary. | `@api-vendor-integration-engineer` | 1, `integrations.gateway` |
| 3 | `src/apiforge/integrations/replay.py` | Create | Load, verify and replay sanitized change bundles without network. | `@api-verification-engineer` | 1, `core.io`, receipt conventions |
| 4 | `src/apiforge/integrations/transport.py` | Create | Explicit read-only transport protocol and typed transport failures. | `@api-vendor-integration-engineer` | 1 |
| 5 | `src/apiforge/application/change_control.py` | Create | Orchestrate bundle → case → critical chain → evaluation → publication. | `@api-agentic-orchestrator` | 1–4, existing application services |
| 6 | `src/apiforge/application/change_errors.py` | Create | Named errors, error-to-result mapping and recovery guidance. | `@api-verification-engineer` | 1, existing error conventions |
| 7 | `src/apiforge/evals/change_control.py` | Create | Golden/holdout recommendation evaluator and metrics aggregation. | `@api-test-strategist` | 1, `AGENT_OUTPUT_CONTRACT.md` |
| 8 | `src/apiforge/observability/change_metrics.py` | Create | Stage timing, terminal state, unresolved and adapter metrics as local artifacts. | `@api-agentic-observability-engineer` | 1, existing JSONL/IO helpers |
| 9 | `src/apiforge/integrations/__init__.py` | Modify | Export the explicit adapter/replay protocols where public. | `@api-vendor-integration-engineer` | 2–4 |
| 10 | `src/apiforge/cli.py` | Modify | Add the public change-control/replay command and governed error boundary. | `@api-agentic-orchestrator` | 5–8 |
| 11 | `src/apiforge/mcp/tools.py` | Modify | Add canonical MCP tool projection for the same use case/result. | `@api-agentic-orchestrator` | 5 |
| 12 | `src/apiforge/surfaces/ide.py` | Modify | Preserve canonical change-control projection for IDE clients. | `@api-dx-docs-reviewer` | 5, 11 |
| 13 | `src/apiforge/surfaces/ui.py` | Modify | Preserve canonical change-control projection for UI clients. | `@api-dx-docs-reviewer` | 5, 11 |
| 14 | `src/apiforge/capabilities/registry.py` | Modify | Validate any additional capability/vertical metadata and verifier paths. | `@api-contract-architect` | 1, 15 |
| 15 | `src/apiforge/rules/capability_matrix.yaml` | Modify | Declare `api.change-control`, `git.read-context` and `cicd.inspect-run` states, limits and verifiers. | `@api-governance-reviewer` | 1–8, docs/tests |
| 16 | `src/apiforge/rules/catalog/routing.yaml` | Modify | Add the missing `discover` + `CONTRACT` route and change-control routing. | `@api-governance-reviewer` | Existing finding taxonomy |
| 17 | `.github/workflows/ci.yml` | Modify | Add artifact-based change-control validation while keeping existing project gates. | `@api-vendor-integration-engineer` | 5, 10, 18 |
| 18 | `.github/workflows/api-change-control.yml` | Create | PR/manual workflow with safe ingress, read-only context and artifact upload. | `@api-vendor-integration-engineer` | 2, 5, 17 |
| 19 | `tests/contracts/test_change_control_contracts.py` | Create | Pydantic schema, hash, redaction and version compatibility tests. | `@api-contract-architect` | 1 |
| 20 | `tests/integrations/test_github_adapter.py` | Create | In-memory transport, endpoint allowlist, status/pagination/error tests. | `@api-vendor-integration-engineer` | 2, 4 |
| 21 | `tests/integrations/test_replay_adapter.py` | Create | Offline replay, tamper, path, missing source and deterministic hash tests. | `@api-verification-engineer` | 3 |
| 22 | `tests/application/test_change_control.py` | Create | Orchestration, error boundary, case artifacts and terminal states. | `@api-governance-reviewer` | 5, 6 |
| 23 | `tests/evals/test_change_control_evaluator.py` | Create | Recommendation schema, golden, holdout and metric behavior. | `@api-test-strategist` | 7, fixtures |
| 24 | `tests/observability/test_change_metrics.py` | Create | Required metrics, redaction, correlation and deterministic output. | `@api-agentic-observability-engineer` | 8 |
| 25 | `tests/e2e/test_api_git_cicd_change_control.py` | Create | PR, manual replay, failure and surface-parity smoke flows. | `@api-verification-engineer` | 5, 7, 10–13 |
| 26 | `tests/rules/test_change_control_routing.py` | Create | `discover` contract route and no-route governed behavior. | `@api-governance-reviewer` | 16 |
| 27 | `tests/fixtures/api_git_cicd/change_bundle.json` | Create | Sanitized representative provider bundle. | `@api-test-strategist` | 1 |
| 28 | `tests/fixtures/api_git_cicd/golden.json` | Create | Reviewed expected recommendation/evidence projection. | `@api-test-strategist` | 1, 7, 27 |
| 29 | `tests/fixtures/api_git_cicd/holdout.yaml` | Create | Missing/inconclusive check and unresolved evidence case. | `@api-test-strategist` | 1, 7 |
| 30 | `tests/fixtures/api_git_cicd/real_anonymized/README.md` | Create | Curation, anonymization and approval rules for real examples. | `@api-security-reviewer` | Security policy |
| 31 | `evals/datasets/api-git-cicd/manifest.yaml` | Create | Dataset manifest, sample hashes, provenance and evaluation version. | `@api-test-strategist` | 27–30 |
| 32 | `docs/capabilities/API_FORGE_CAPABILITY_MATRIX.md` | Modify | Document new capabilities, support states, limitations and verifiers. | `@api-dx-docs-reviewer` | 15, 26 |
| 33 | `docs/guides/API_FORGE_PLATFORM_USAGE.md` | Modify | Document PR/manual commands, replay, artifacts and governed failures. | `@api-dx-docs-reviewer` | 5, 10, 18 |
| 34 | `docs/security/api-git-cicd-control-plane.md` | Create | Threat model, fork/token policy, redaction and mutation boundary. | `@api-security-reviewer` | 2, 4, 18 |
| 35 | `docs/architecture/API_FORGE_API_GIT_CICD_CONTROL_PLANE.md` | Create | Public architecture and provenance model. | `@api-architecture-reviewer` | 1–18 |
| 36 | `docs/agents/AGENT_OUTPUT_CONTRACT.md` | Modify | Clarify recommendation evaluation and evidence requirements if needed. | `@api-agentic-orchestrator` | 7, 23 |
| 37 | `README.md` | Modify | Public command, CI artifact and support-boundary documentation. | `@api-dx-docs-reviewer` | 10, 17, 32–35 |

**Total Files:** 37 (18 create, 19 modify; exact file count may be reduced during build if an existing helper safely satisfies a manifest item without weakening a contract.)

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| `@api-contract-architect` | 1, 14, 19 | OpenAPI/change contracts, versioning and typed schema boundary. |
| `@api-vendor-integration-engineer` | 2, 4, 9, 17, 18, 20 | Provider adapter and read-only integration boundary; the project profile explicitly treats vendor integrations as optional and read-only. |
| `@api-verification-engineer` | 3, 21, 25 | Independent replay, receipts, hashes and proof axes. |
| `@api-agentic-orchestrator` | 5, 10, 11, 36 | Supervisor/use-case orchestration, TaskSpec/capability surfaces and agent handoff. |
| `@api-governance-reviewer` | 15, 16, 22, 26 | Contract/code divergence, breaking changes, lifecycle routing and governed terminal states. |
| `@api-test-strategist` | 7, 23, 27–29, 31 | Contract tests, fixtures, goldens, holdouts and evidence needed to prove behavior. |
| `@api-agentic-observability-engineer` | 8, 24 | Stage evidence, metrics, correlation and independent verification. |
| `@api-security-reviewer` | 30, 34 | Untrusted PR input, token/fork policy, redaction and provider threat model. |
| `@api-dx-docs-reviewer` | 12, 13, 32, 33, 37 | Consistent consumer-facing projections, examples and public limits. |
| `@api-architecture-reviewer` | 35 | Architecture review against evidence and explicit blind spots. |
| `(general)` | None | Every planned file has a project specialist; no general fallback is needed. |

**Agent Discovery:** Scanned the project `agents/**/*.md` profiles and their `.claude/agents/` mirrors. Matching used purpose keywords, rule areas, existing project boundaries and the KB domains `python`, `pydantic`, `testing` and `genai`.

---

## Code Patterns

### Pattern 1: Versioned Pydantic boundary

Use a strict, immutable model for data crossing the provider/application boundary. The model is the only accepted input to the application; raw provider dictionaries stay inside the adapter.

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: str
    kind: Literal["pr", "diff", "check", "artifact", "manual"]
    reference: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    observed_at: str


class ChangeBundle(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["af-change-bundle/1"]
    repository: str = Field(min_length=1)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    head_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    origin: Literal["pull_request", "branch", "manual", "replay"]
    sources: tuple[SourceRef, ...] = ()
    limitations: tuple[str, ...] = ()


def parse_bundle(value: object) -> ChangeBundle:
    """Validate external data before it reaches the application layer."""
    return ChangeBundle.model_validate(value)
```

This follows the Pydantic KB: `extra="forbid"`, constrained fields, immutable models and `model_validate` at the boundary.

### Pattern 2: Read-only adapter with injected transport

The transport protocol exposes only read operations. The application depends on the adapter protocol, not on HTTP or a provider SDK.

```python
from collections.abc import Mapping
from typing import Protocol


class ReadOnlyTransport(Protocol):
    def get_json(self, path: str, *, params: Mapping[str, str] = ()) -> object: ...


class ProviderAdapter(Protocol):
    name: str

    def collect(self, request: object) -> object: ...


class GitHubReadOnlyAdapter:
    name = "github-read-only"
    _ALLOWED_PATHS = frozenset({"pull", "diff", "checks", "artifacts"})

    def __init__(self, transport: ReadOnlyTransport) -> None:
        self._transport = transport

    def collect(self, request: object) -> object:
        # Resolve and validate only allowlisted GET paths; return ChangeBundle.
        # The concrete implementation must never expose write methods.
        return self._collect_bundle(request)

    def _collect_bundle(self, request: object) -> object:
        raise NotImplementedError
```

Production transport creation belongs to the explicit CI host entrypoint; tests pass an in-memory fake. This keeps the core free of provider SDKs and makes endpoint usage auditable.

### Pattern 3: Governed error boundary

Expected boundary failures are represented as data. The CLI catches only the application error family and emits the canonical result; unexpected failures are named as operational errors rather than printed as a traceback.

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChangeControlError(Exception):
    code: str
    message: str
    retryable: bool = False
    unlock: str = "inspect the persisted diagnostic"

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def execute_safely(run: object) -> dict[str, object]:
    try:
        return run.execute()  # type: ignore[union-attr]
    except ChangeControlError as exc:
        return {
            "status": "blocked" if exc.code.endswith("AUTH") else "review",
            "error_code": exc.code,
            "gaps": [exc.unlock],
        }
    except (OSError, ValueError, TypeError) as exc:
        return {
            "status": "failed",
            "error_code": "AF-CHANGE-OPERATIONAL",
            "gaps": [str(exc)],
        }
```

The final implementation should use the project’s existing typed result models rather than returning an unvalidated dictionary; the snippet shows the control-flow shape only.

### Pattern 4: Replayable metrics event

Metrics are artifacts, not an implicit network side effect. Use immutable records and atomic JSONL writing already present in the project.

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChangeStageMetric:
    run_id: str
    case_id: str
    stage: str
    status: str
    duration_ms: int
    unresolved_count: int
    artifact_refs: tuple[str, ...]
    error_code: str | None = None
```

Every event is correlated by run and case, redacted before writing and bound to the final receipt.

### Pattern 5: Safe workflow ingress

The workflow passes context as data and uploads artifacts. It does not grant a privileged token to code from an untrusted PR or call a mutating provider action.

```yaml
name: API change control

on:
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: read
  checks: read
  actions: read

jobs:
  collect-and-analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run read-only change control
        env:
          APIFORGE_CHANGE_ORIGIN: ${{ github.event_name }}
          APIFORGE_REPOSITORY: ${{ github.repository }}
          APIFORGE_BASE_SHA: ${{ github.event.pull_request.base.sha || github.event.before }}
          APIFORGE_HEAD_SHA: ${{ github.event.pull_request.head.sha || github.sha }}
        run: python -m apiforge change-control run --out-dir .apiforge/change-control
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: api-forge-change-control
          path: .apiforge/change-control
```

The exact fork policy and token handling must be finalized in the workflow implementation; the workflow cannot be treated as proof that the provider check succeeded.

---

## Data Flow

```text
1. Ingress identifies PR/branch/manual origin and base/head refs.
   │
   ▼
2. Policy selects GitHub read-only collection or local artifact replay.
   │
   ▼
3. Adapter validates, redacts and hashes source payloads into ChangeBundle/v1.
   │
   ▼
4. Application creates an isolated case and records provider evidence metadata.
   │
   ▼
5. Existing chain runs: analyze → next-step → graph → evidence → brief.
   │
   ▼
6. Evaluator validates recommendation contract and compares golden/holdout expectations.
   │
   ▼
7. Publisher emits result, findings, graph, receipt, recommendation, JUnit and metrics.
   │
   ▼
8. CI uploads artifacts; CLI/MCP/IDE/UI project the same CapabilityResult.
```

### Artifact layout

```text
.apiforge/change-control/<run-id>/
├── input/change-bundle.json
├── input/sources.jsonl
├── case/case.json
├── case/api-ir.json
├── case/facts.json
├── case/findings.json
├── graph/nodes.jsonl
├── graph/edges.jsonl
├── evidence/receipt.json
├── recommendation/agent-artifact.json
├── evaluation/result.json
├── metrics/stages.jsonl
├── test-results.xml
└── outcome-brief.json
```

The manifest is written last. Every declared artifact has a SHA-256 reference; a missing, divergent or unsafe path prevents the run from being considered complete.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| GitHub Pull Requests | Explicit read-only adapter over allowlisted GET transport | CI-provided read-only token when policy permits; no token values persisted |
| GitHub Checks | Read-only observation of check status/conclusion/SHA | Same read-only provider boundary |
| GitHub Actions artifacts | Read-only metadata/reference collection; workflow upload is the CI publisher | CI runtime identity; adapter does not mutate through provider API |
| GitHub Actions runner | Process host for CLI and artifact upload | Workflow permissions; no persistent API Forge service |
| CLI | Local command entrypoint | Filesystem case and optional explicit provider configuration |
| MCP | Canonical tool projection | Caller supplies request; no separate semantics |
| IDE/UI | Canonical result projection or downloaded artifacts | Local/MCP bridge; no write authority |

The provider adapter must preserve HTTP status, source URL/reference, observed time, response hash and limitation. Rate limits, missing scopes and inaccessible artifacts become named unresolved evidence.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Pydantic contracts, hashes, redaction, typed errors and metrics | `tests/contracts/test_change_control_contracts.py`, `tests/observability/test_change_metrics.py` | pytest, Pydantic model validation | All schema/error branches and secret cases |
| Unit | Adapter allowlist and transport behavior | `tests/integrations/test_github_adapter.py` | pytest fake transport | Every endpoint, malformed response, status and no-write invariant |
| Unit | Replay/tamper/path safety | `tests/integrations/test_replay_adapter.py` | pytest temporary paths | Valid replay plus hash/path/missing-artifact failures |
| Application integration | Bundle to case and governed terminal states | `tests/application/test_change_control.py` | pytest fixtures, existing application services | All expected error codes and chain artifacts |
| Routing integration | Contract findings in discover/verify | `tests/rules/test_change_control_routing.py` | pytest, routing catalog | Correct agent and explicit no-route gap |
| Evaluation | Recommendation contract, golden and holdout | `tests/evals/test_change_control_evaluator.py` | pytest, fixture manifest | No optimistic holdout result; deterministic golden projection |
| Surface integration | CLI/MCP/IDE/UI parity | `tests/e2e/test_api_git_cicd_change_control.py` | Typer runner, direct surface calls | Same canonical state/evidence/gaps/error codes |
| E2E smoke | PR-like, manual replay and failure flows | `tests/e2e/test_api_git_cicd_change_control.py` | pytest, sanitized bundles | 3 primary flows complete without traceback |
| CI workflow validation | YAML shape, permissions, artifact path and command | workflow tests or static parser in existing CI | YAML parser, shell-free checks | No write permissions and always-upload behavior |
| Independent verification | Receipt, hashes and report correspondence | existing verification tests + new replay tests | verifier services | Acceptance does not rely on same producer only |

### Acceptance coverage map

| Acceptance tests | Primary verifier |
|------------------|------------------|
| AT-001, AT-002, AT-008, AT-014 | `tests/e2e/test_api_git_cicd_change_control.py` |
| AT-003, AT-004, AT-005, AT-015 | `tests/integrations/test_github_adapter.py`, `tests/application/test_change_control.py` |
| AT-006, AT-007, AT-010 | `tests/rules/test_change_control_routing.py`, `tests/evals/test_change_control_evaluator.py` |
| AT-009, AT-012 | `tests/contracts/test_change_control_contracts.py`, `tests/integrations/test_replay_adapter.py` |
| AT-011 | `tests/e2e/test_api_git_cicd_change_control.py` |
| AT-013 | `tests/contracts/test_change_control_contracts.py`, `tests/integrations/test_github_adapter.py` |

The build must add at least one sanitized real example before claiming the external-evidence criterion complete. Synthetic fixture coverage alone is not sufficient for the final ship gate.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Missing/insufficient token | Return `AF-GITHUB-AUTH`, persist policy gap and stop provider collection; allow local replay if bundle exists. | No automatic credential retry |
| Invalid provider payload | Return `AF-GITHUB-PAYLOAD`, preserve source reference without raw secret-bearing content and mark input invalid. | No |
| Provider rate limit/transient GET failure | Return `AF-GITHUB-TRANSIENT` with observed status and retry guidance; bounded transport retry may be configured outside the core. | Policy-bounded only |
| Inaccessible check/artifact | Continue with explicit `unresolved` evidence if the core chain is still valid; never infer success. | No silent retry |
| Unsupported provider | Return `AF-INTEGRATION-UNSUPPORTED` and capability `unsupported`. | No |
| Unsafe path or input/output overlap | Reuse existing path guards and return named case/sandbox error. | No |
| Secret detected during normalization | Return `AF-CHANGE-SECRET`, do not publish the unsafe artifact, and retain only safe diagnostic metadata. | No |
| Route missing in catalog | Return `AF-ROUTING-NO-ROUTE` with dominant area, phase and unlock; do not select an agent by guess. | No |
| Receipt/hash mismatch | Return `AF-EVIDENCE-MISMATCH`; block completion and identify the divergent artifact. | No |
| Unexpected application exception | Catch at CLI/workflow boundary, persist `AF-CHANGE-OPERATIONAL` with correlation id and sanitized message, exit with governed failure code. | No blind retry |

All exceptions are chained internally for diagnostics but never serialized with tokens, headers, signed URLs or raw provider payloads.

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `APIFORGE_CHANGE_ORIGIN` | enum | required | `pull_request`, `branch`, `manual` or `replay`. |
| `APIFORGE_CHANGE_OUT_DIR` | path | `.apiforge/change-control` | Isolated artifact root; input/output overlap is refused. |
| `APIFORGE_GITHUB_API_URL` | URL | provider-configured | Read-only API base; must pass an explicit allowlist. |
| `APIFORGE_GITHUB_READ_ONLY_TOKEN` | secret | absent | Optional host credential; never written to case, logs or artifacts. |
| `APIFORGE_CHANGE_BUNDLE` | path | absent | Sanitized bundle for artifact-first/replay mode. |
| `APIFORGE_UNTRUSTED_PR_POLICY` | enum | `no_secret_replay` | Behavior for forks/untrusted events; fail closed when not configured. |
| `APIFORGE_PUBLISH_MODE` | enum | `artifacts` | MVP accepts only local/CI artifacts; provider writes are rejected. |
| `APIFORGE_EVAL_DATASET` | path | fixture dataset | Manifest of fixture, golden, holdout and anonymized real cases. |
| `APIFORGE_METRICS_FORMAT` | enum | `jsonl` | Local append-only metrics artifact; JUnit remains an additional test projection. |
| `APIFORGE_FAIL_POLICY` | enum | `governed` | Maps confirmed blocking findings and operational errors to CI exit behavior without rewriting capability state. |

Configuration is loaded once at the host boundary, validated, redacted from diagnostics and passed as immutable values to the application.

---

## Security Considerations

- **Least privilege:** the provider integration exposes only read operations. The workflow declares read-only permissions and the adapter rejects non-allowlisted paths/methods before transport invocation.
- **Untrusted PR boundary:** do not run privileged secrets or mutating actions in the same execution boundary as untrusted PR code. Fork/missing-token paths use event data or artifact replay and degrade to `review`/`blocked`/`unresolved`.
- **No target code execution:** static analysis, bundle normalization and replay treat source as data. The design does not invoke application code, install arbitrary dependencies or connect to project databases/cloud resources.
- **Secret redaction:** redact token-shaped values, authorization headers, signed URLs, environment values and provider secrets before facts, logs, JUnit, Markdown, JSON, metrics or receipts are written. Secret detection failure blocks publication.
- **Path safety:** reuse case/sandbox path traversal, symlink and input/output overlap guards. Provider file names and artifact paths are untrusted.
- **Hash provenance:** bind source payloads and generated artifacts to SHA-256 references. A receipt proves correspondence, never authorship or provider truth.
- **Replay safety:** replay accepts only a validated bundle and refuses hash divergence, missing declared artifacts or schema versions outside the supported range.
- **Capability states:** `heuristic`, `unresolved` and `unsupported` remain visible; no missing check becomes a passing gate.
- **Mutation gate:** `apply` requests, comments, statuses, merge, push and deploy remain blocked by the integration gateway unless a future feature introduces explicit policy, approval, rollback and receipt.
- **Dependency hygiene:** no provider SDK/model SDK is added to `src/`; external transport dependencies, if needed, are isolated and justified in the build report.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured, sanitized records keyed by `run_id`, `case_id`, stage and `error_code`; raw provider payloads and secrets are never logged. |
| Metrics | `metrics/stages.jsonl` plus a summary JSON with origin, base/head SHAs, stage durations, terminal state, unresolved count, adapter failures and artifact refs. |
| Tracing | Deterministic stage records (`collect`, `normalize`, `analyze`, `route`, `graph`, `evidence`, `evaluate`, `publish`) with start/end/status; no external tracing backend required for MVP. |
| Correlation | Every provider source, case artifact, recommendation and metric points to the same `run_id`/`case_id`; receipt binds the final artifact set. |
| Alerting | CI exit policy distinguishes `blocked`, `review` and operational `failed`; no dashboard or notification service is introduced in this feature. |
| Retention | CI artifact retention is controlled by the host; local replay requires the bundle and its referenced artifacts to remain available. |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | design-agent | Architecture, decisions, manifest, KB patterns, testing, security and observability for the approved DEFINE. |
| 1.1 | 2026-09-22 | ship-agent | Design shipped and archived; implementation coverage and unresolved proof gaps remain documented in BUILD_REPORT. |

---

## Next Step

**Shipped by:** `/ship .claude/sdd/features/DEFINE_API_GIT_CICD_CHANGE_CONTROL_PLANE.md`
