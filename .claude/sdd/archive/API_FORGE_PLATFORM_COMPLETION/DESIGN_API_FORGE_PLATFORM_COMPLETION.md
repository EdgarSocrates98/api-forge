# DESIGN: API Forge Platform Completion

> Design técnico para corrigir os gaps críticos e consolidar a API Forge como
> uma plataforma determinística, evidence-first e extensível de engenharia de
> software. A plataforma recomenda boas práticas e arquiteturas com base na
> necessidade declarada e no contexto observado; não depende de um wizard nem
> converte hipóteses em fatos.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_PLATFORM_COMPLETION |
| **Date** | 2026-09-22 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_PLATFORM_COMPLETION.md](./DEFINE_API_FORGE_PLATFORM_COMPLETION.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                         API FORGE CONTROL PLANE                           │
├──────────────────────────────────────────────────────────────────────────┤
│  CLI             MCP             IDE bridge              UI projection     │
│   │               │                  │                       │             │
│   └───────────────┴──────────────────┴───────────────────────┘             │
│                   Canonical CapabilityRequest/Result                      │
│                                  │                                        │
│                 Intent + context + persisted case                         │
│                                  │                                        │
│       Deterministic supervisor / state machine / policy engine             │
│          │                 │                    │                          │
│   static extractors    specialist agents    integration gateway            │
│   rules + IRs          structured output    Git/CI/cloud/data/messaging     │
│          │                 │                    │                          │
│          └─────────────────┴────────────────────┘                          │
│             sandbox + read-only boundary + approval gates                  │
│                                  │                                        │
│     case artifacts → evidence receipt → provenance graph → OutcomeBrief   │
└──────────────────────────────────────────────────────────────────────────┘
```

The design preserves the current separation between deterministic analysis,
agentic orchestration and external adapters:

1. A surface normalizes input into a canonical request. It must not implement
   its own routing rules, capability claims or finding interpretation.
2. The application layer loads or creates the case, validates the request and
   selects a deterministic operation. The existing `TaskSpec`, `AgenticRun`,
   `AgentArtifact`, `Receipt`, `GraphExport` and `OutcomeBrief` contracts stay
   authoritative.
3. Static extractors and rules produce facts, diagnostics and findings. A
   missing binding, dynamic route, missing tool or unavailable provider becomes
   an explicit state such as `unresolved`, `not_observed`, `refused` or
   `unsupported`.
4. The supervisor may call an agent through the existing adapter boundary, but
   every response is validated as structured data. Agents can recommend
   techniques, patterns and architectures only when they cite available facts,
   distinguish assumptions, and name the verifier for the recommendation.
5. External integrations are adapters behind a gateway. Read operations are the
   default. Git patches, CI triggers, cloud changes, database writes,
   publications and broker mutations require a persisted policy decision,
   approval, evidence and rollback plan.
6. Every terminal path produces a contract payload and a receipt or a governed
   error. Normal CLI output never leaks an uncontrolled traceback; debug detail
   is retained only when an explicit debug mode is enabled and is itself
   associated with the case/run.

Dependency direction is one-way: surfaces → application/contracts →
deterministic engines and runtime → adapters. Agents depend on contracts and
knowledge, not on provider SDKs. Verification reads persisted artifacts and
does not accept the same artifact that originated a decision as independent
proof. There are no shared deployable dependencies between the core and the
future visual or provider-specific surfaces.

### Design boundaries

The first build wave is the smallest complete foundation that makes the
critical chain reliable and establishes the contract for all later verticals.
The same design also defines extension points for Git, CI/CD, IDE, visual UI,
cloud, databases, messaging, observability and front-end analysis. A provider
without a verified adapter remains `unsupported` or `unresolved`; the platform
must not advertise production support merely because an interface exists.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Surface contract layer | Normalize CLI, MCP, IDE and UI requests and project the same result | Pydantic v2, JSON |
| Case and artifact layer | Persist immutable inputs, hashes, facts, findings and diagnostics | Existing case service, JSON, SHA-256 |
| FastAPI static extractor | Resolve literal bindings and emit unresolved diagnostics for dynamic or missing references | Python AST/static scan |
| Findings router | Select specialist agents from the official findings envelope and catalog | Existing `application.next_step` |
| Capability registry | Publish support state, evidence requirements, limits, risks, rollback and verifier | YAML + Pydantic contracts |
| Agent guardrail | Validate structured recommendations, evidence references, assumptions and unresolved claims | `AgentArtifact/v1`, Pydantic validators |
| Deterministic supervisor | Orchestrate bounded specialist calls and state transitions | Existing runtime supervisor, TaskSpec, policy |
| Integration gateway | Isolate Git, CI/CD, cloud, database, messaging and vendor adapters | Protocols, read-only default, policy gates |
| Evidence chain | Emit receipts, provenance graph and outcome brief from persisted artifacts | Existing evidence, graph and brief services |
| Platform lab | Execute the six required vertical fixtures, golden cases and holdouts | Pytest, YAML manifests, local fixtures |
| Knowledge and agent layer | Teach agents how to reason and verify without moving policy into prompts | Project skills, local agents, KB references |
| Documentation layer | Document every public capability, limitation, evidence boundary and verifier | Markdown, generated contract references |

---

## Key Decisions

### Decision 1: Foundation-first vertical slices

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The platform has a broad strategic scope, but the current
auto-analysis is blocked by a FastAPI extractor failure, and the public
`next-step` command does not consume its own generated envelope. Adding more
providers before fixing these boundaries would make the support matrix less
trustworthy.

**Choice:** Build in waves: (1) safe critical chain and CLI error boundary,
(2) canonical capability and agent-output contracts, (3) one fixture/golden/
holdout for each initial vertical, (4) parity projections and integration
gateway, and (5) provider-specific adapters behind the gateway.

**Rationale:** Every later vertical inherits a proven execution, evidence and
verification path. The six verticals remain in the product scope, while the
core stays small enough to audit and roll back.

**Alternatives Rejected:**
1. A monolithic first release covering every provider - rejected because it
   would couple unverified integrations to the deterministic core.
2. Continue adding specializations before fixing the chain - rejected because
   it would increase the number of unsupported paths without improving trust.

**Consequences:**
- The first build wave contains extension contracts and representative local
  adapters, not every vendor implementation.
- Each later provider must add its own fixture, golden, holdout, documentation
  and verifier before it can move to `supported`.

---

### Decision 2: Canonical capability state and evidence contract

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** A parser, an agent prompt and a provider adapter are currently
easy to mistake for production capability. The DEFINE requires a public
matrix that distinguishes support from heuristics and missing proof.

**Choice:** Add a versioned platform contract with capability states
`supported`, `heuristic`, `unresolved` and `unsupported`. Each record contains
the vertical, operation, evidence references, limitations, prerequisites,
risk, rollback, verifier and supported surfaces. The record is registered in
the existing contract registry and loaded from a deterministic YAML matrix.

**Rationale:** A single state vocabulary can be projected by CLI, MCP, IDE and
UI without each surface inventing its own confidence semantics. The contract
also makes documentation and lab coverage machine-checkable.

**Alternatives Rejected:**
1. Boolean `supported` flags - rejected because they collapse heuristics and
   unknown external posture into a false promise.
2. Free-form agent text - rejected because it cannot drive deterministic gates
   or parity tests.

**Consequences:**
- New public capabilities cannot be registered without a verifier and
  limitations.
- Existing `Capability/v1` remains available for observability vendor
  adapters; the new platform record is not a breaking replacement.

---

### Decision 3: Normalize official artifact envelopes at the boundary

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The generated `findings.json` is an object with a `findings` list,
while the public CLI currently validates the whole object as a tuple of
findings. The dispatch path already demonstrates the correct envelope
normalization.

**Choice:** Introduce one strict loader for list-or-envelope compatibility,
accept the official `{"findings": [...]}` form, reject malformed payloads with
a typed `AF-*` error, and use it from CLI, MCP and dispatch. The compatibility
form is transitional and emits no guessed data.

**Rationale:** Normalization belongs at the input boundary, not in
`application.next_step`, whose contract is already a tuple of `Finding`.
Keeping the application service pure avoids coupling it to file formats.

**Alternatives Rejected:**
1. Change `findings.json` to a bare list - rejected because graph, evidence and
   existing consumers rely on the official envelope.
2. Catch `KeyError` or `ValidationError` and return an empty list - rejected
   because it would hide findings and falsify routing.

**Consequences:** The same loader becomes a reusable pattern for other public
artifact envelopes. A malformed artifact is a governed failure with a stable
code and no partial specialist recommendation.

---

### Decision 4: Unresolved static references are diagnostics, never indexing errors

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The FastAPI resolver can return a reference whose binding is not
present in the local binding map. The traversal then indexes `bindings[key]`
and leaks a `KeyError` for code that is valid input to the offline analyzer but
not statically resolvable.

**Choice:** Guard every resolver/traversal boundary. If an app, router or
include target is absent from the binding index, emit a deterministic
`AF-FASTAPI-UNRESOLVED-BINDING` diagnostic with source and line, skip that
branch, and continue producing the rest of the inventory. The result remains
usable only to the extent represented by its facts and diagnostics.

**Rationale:** This follows the existing extractor contract and preserves the
distinction between observed routes and unresolved code.

**Alternatives Rejected:**
1. Synthesize a router or route - rejected because it would invent facts.
2. Abort the entire analysis - rejected because one unresolved branch should
   not discard independent static evidence.

**Consequences:** The extractor and index command become total over their
   declared static input domain. A holdout must exercise the missing-binding
   case so the regression cannot return.

---

### Decision 5: Supervisor plus bounded specialists, not a monolithic agent

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** The user wants agents that understand the need and suggest
techniques and architectures, but the repository contract requires the
supervisor, TaskSpec, policy and verifier to remain deterministic.

**Choice:** Keep the deterministic supervisor as the only authority for
scope, routing, budgets, state transitions, tool allowlists and external
mutation gates. Specialists receive a bounded context and return
`AgentArtifact/v1` with recommendation, facts, assumptions, risks, unresolved
items and verifier references. The existing local agent fleet remains the
semantic specialization layer.

**Rationale:** Specialized agents with explicit handoffs are easier to test,
review and replace than one agent with every tool. The architecture benefits
from model-independent contracts and can use the fake adapter in local CI.

**Alternatives Rejected:**
1. Give agents direct provider SDK access - rejected by the offline-first and
   policy constraints.
2. Encode all best practices in a single prompt - rejected because prompts
   cannot enforce schemas, permissions, evidence lineage or rollback.

**Consequences:** Agent quality is measured using facts, holdouts and mutation
   checks. Prompt improvements cannot bypass a deterministic verification gate.

---

### Decision 6: External integrations are capability-gated adapters

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Git, CI/CD, IDE, UI, cloud, databases, messaging and vendor
systems all have different credentials, side effects and failure modes.

**Choice:** Define a provider-neutral integration gateway with read, plan,
apply and verify phases. Read and plan are safe defaults. Apply is refused
unless the adapter declares risk, the policy permits it, an approval gate is
recorded, and a rollback is available. Provider modules never become imports
of the deterministic core.

**Rationale:** This creates one safety model across all external systems and
allows a local fake adapter to prove orchestration without live infrastructure.
It also makes `unsupported` a valid, useful answer rather than an implicit
best-effort execution.

**Alternatives Rejected:**
1. Call CLIs or SDKs directly from agents - rejected because credentials and
   mutations would escape the policy boundary.
2. Treat all integrations as read-only forever - rejected because the long-term
   platform needs controlled change plans, but mutation must remain gated.

**Consequences:** Each provider adapter must ship a capability record,
read-only fixture, negative/gate test and rollback documentation before
promotion.

---

### Decision 7: Independent verification and stale-evidence detection

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Existing SDD and release evidence can become stale after source,
contract or configuration changes. A passing historical artifact is not proof
of the current checkout.

**Choice:** The completion gate recomputes hashes, executes focused chain
tests, validates the vertical lab, runs the relevant static checks and records
the current SDD/release evidence. The verifier is independent from the
producer and refuses `DONE` while gaps, stale references or missing holdouts
remain.

**Rationale:** This is consistent with `OutcomeBrief` and the repository's
evidence-first operating contract. It makes the platform honest about what it
has and has not proven.

**Alternatives Rejected:**
1. Trust a committed report without recomputation - rejected because it can be
   stale or detached from the current inputs.
2. Make external tools mandatory for all local checks - rejected because the
   offline core must report unavailable tools as an explicit limitation.

**Consequences:** Release can remain `REVIEW` or `BLOCKED` even when unit tests
pass if independent proof is absent. That is an intentional safety property.

---

## File Manifest

The manifest is intentionally divided into foundation, contracts, surfaces,
vertical labs and documentation. Provider-specific integrations are not
silently listed as complete: they are represented by the gateway and matrix
until a provider has its own evidence bundle.

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/adapters/fastapi/extractor.py` | Modify | Guard missing bindings and emit unresolved diagnostics | `@api-contract-architect` | None |
| 2 | `src/apiforge/cli.py` | Modify | Normalize findings envelopes and govern CLI failures | `@api-contract-architect` | 1, 7 |
| 3 | `src/apiforge/mcp/tools.py` | Modify | Use the same artifact loader and surface contracts as CLI | `@api-agentic-orchestrator` | 2, 7 |
| 4 | `src/apiforge/dispatch/runner.py` | Modify | Route public dispatch through canonical capability and artifact boundaries | `@api-agentic-orchestrator` | 2, 7 |
| 5 | `src/apiforge/contracts/platform.py` | Create | Versioned capability, request, result and vertical-coverage models | `@api-contract-architect` | None |
| 6 | `src/apiforge/contracts/__init__.py` | Modify | Export platform contracts without breaking existing imports | `@api-contract-architect` | 5 |
| 7 | `src/apiforge/contracts/registry.py` | Modify | Register platform contracts for schema and parity checks | `@api-contract-architect` | 5, 6 |
| 8 | `src/apiforge/capabilities/__init__.py` | Create | Public capability registry package | `@api-platform-selector` | 5 |
| 9 | `src/apiforge/capabilities/registry.py` | Create | Load and validate the capability matrix | `@api-platform-selector` | 5, 8, 18 |
| 10 | `src/apiforge/capabilities/verify.py` | Create | Verify documentation, limits, evidence and verifier per capability | `@api-verification-engineer` | 9, 18, 25 |
| 11 | `src/apiforge/rules/capability_matrix.yaml` | Create | Machine-readable support matrix for all public surfaces and verticals | `@api-platform-selector` | 5 |
| 12 | `src/apiforge/runtime/guardrails.py` | Create | Validate and reject ungrounded agent artifacts | `@api-agentic-orchestrator` | 5, 13 |
| 13 | `src/apiforge/runtime/supervisor.py` | Modify | Enforce structured agent output, budgets and verifier handoff | `@api-agentic-orchestrator` | 5, 12 |
| 14 | `src/apiforge/integrations/__init__.py` | Create | Integration gateway package | `@api-vendor-integration-engineer` | 5 |
| 15 | `src/apiforge/integrations/gateway.py` | Create | Read/plan/apply/verify adapter protocol and policy gate | `@api-vendor-integration-engineer` | 5, 14 |
| 16 | `src/apiforge/integrations/git.py` | Create | Read-only Git context and gated patch plan adapter | `@api-vendor-integration-engineer` | 15 |
| 17 | `src/apiforge/integrations/cicd.py` | Create | CI/CD metadata, report and gated execution adapter | `@api-operations-engineer` | 15 |
| 18 | `src/apiforge/integrations/cloud.py` | Create | Cloud posture read adapter and gated plan boundary | `@aws-api-infra-reviewer` | 15 |
| 19 | `src/apiforge/integrations/data.py` | Create | Database/schema/access read adapter boundary | `@api-data-access-architect` | 15 |
| 20 | `src/apiforge/integrations/messaging.py` | Create | Broker/topic/queue read adapter boundary | `@api-event-driven-architect` | 15 |
| 21 | `src/apiforge/surfaces/__init__.py` | Create | Surface projection package | `(general)` | 5 |
| 22 | `src/apiforge/surfaces/projection.py` | Create | Canonical projection shared by CLI, MCP, IDE and UI | `@api-agentic-orchestrator` | 5, 21 |
| 23 | `src/apiforge/surfaces/ide.py` | Create | JSON-RPC/stdio IDE projection with no provider mutation | `@api-dx-docs-reviewer` | 22 |
| 24 | `src/apiforge/surfaces/ui.py` | Create | Framework-neutral UI data projection and action gates | `@api-dx-docs-reviewer` | 22 |
| 25 | `agents/api-platform-completion-reviewer.md` | Create | Specialist for capability support, evidence and parity review | `@api-verification-engineer` | 5, 10 |
| 26 | `.agents/skills/api-forge-platform-completion/SKILL.md` | Create | Operational skill for platform completion and evidence discipline | `@api-forge-verification` | 10, 25 |
| 27 | `tests/adapters/test_fastapi_extractor.py` | Create | Regression for missing-binding and dynamic-route holdouts | `@api-test-strategist` | 1 |
| 28 | `tests/e2e/test_platform_completion.py` | Create | Full `analyze → next-step → graph → evidence → brief` smoke flow | `@api-test-strategist` | 1–24 |
| 29 | `tests/e2e/test_next_step.py` | Modify | Official findings envelope and malformed-input coverage | `@api-test-strategist` | 2 |
| 30 | `tests/dispatch/test_runner.py` | Modify | CLI/dispatch parity and governed error envelopes | `@api-test-strategist` | 2, 4, 22 |
| 31 | `tests/mcp/test_tools.py` | Modify | MCP/CLI contract parity | `@api-test-strategist` | 3, 22 |
| 32 | `tests/runtime/test_supervisor.py` | Modify | Agent guardrails, evidence grounding and mutation gates | `@api-test-strategist` | 12, 13, 15 |
| 33 | `tests/labs/platform_verticals.yaml` | Create | Six-vertical fixture/golden/holdout manifest | `@api-test-strategist` | 34–55 |
| 34 | `tests/labs/test_platform_verticals.py` | Create | Execute and validate the vertical coverage contract | `@api-verification-engineer` | 33, 56 |
| 35 | `tests/fixtures/platform/api/openapi.yaml` | Create | API example project contract fixture | `@api-contract-architect` | None |
| 36 | `tests/fixtures/platform/api/app.py` | Create | API example project implementation fixture | `@api-contract-architect` | 35 |
| 37 | `tests/fixtures/platform/api/golden.json` | Create | Expected API analysis result | `@api-verification-engineer` | 35, 36 |
| 38 | `tests/fixtures/platform/api/holdout.yaml` | Create | API unresolved/negative case | `@api-test-strategist` | 35, 36 |
| 39 | `tests/fixtures/platform/database/schema.sql` | Create | Database schema and migration fixture | `@api-data-access-architect` | None |
| 40 | `tests/fixtures/platform/database/repository.py` | Create | Database access-pattern fixture | `@api-data-access-architect` | 39 |
| 41 | `tests/fixtures/platform/database/golden.json` | Create | Expected database analysis result | `@api-verification-engineer` | 39, 40 |
| 42 | `tests/fixtures/platform/database/holdout.yaml` | Create | Database missing-evidence/unsafe-access case | `@api-test-strategist` | 39, 40 |
| 43 | `tests/fixtures/platform/messaging/asyncapi.yaml` | Create | Messaging contract fixture | `@api-event-driven-architect` | None |
| 44 | `tests/fixtures/platform/messaging/consumer.py` | Create | Producer/consumer and retry fixture | `@api-event-driven-architect` | 43 |
| 45 | `tests/fixtures/platform/messaging/golden.json` | Create | Expected messaging analysis result | `@api-verification-engineer` | 43, 44 |
| 46 | `tests/fixtures/platform/messaging/holdout.yaml` | Create | Messaging lag/DLQ/ordering unresolved case | `@api-test-strategist` | 43, 44 |
| 47 | `tests/fixtures/platform/cicd/pipeline.yaml` | Create | CI/CD pipeline fixture | `@api-operations-engineer` | None |
| 48 | `tests/fixtures/platform/cicd/golden.json` | Create | Expected CI/CD analysis result | `@api-verification-engineer` | 47 |
| 49 | `tests/fixtures/platform/cicd/holdout.yaml` | Create | CI/CD missing-gate case | `@api-test-strategist` | 47 |
| 50 | `tests/fixtures/platform/cloud/main.tf` | Create | Terraform/cloud posture fixture | `@terraform-reviewer` | None |
| 51 | `tests/fixtures/platform/cloud/golden.json` | Create | Expected cloud analysis result | `@api-verification-engineer` | 50 |
| 52 | `tests/fixtures/platform/cloud/holdout.yaml` | Create | Cloud unresolved-variable/read-only case | `@api-test-strategist` | 50 |
| 53 | `tests/fixtures/platform/frontend/package.json` | Create | Front-end project metadata fixture | `@api-dx-docs-reviewer` | None |
| 54 | `tests/fixtures/platform/frontend/src/api.ts` | Create | Front-end/API integration fixture | `@api-dx-docs-reviewer` | 53 |
| 55 | `tests/fixtures/platform/frontend/golden.json` | Create | Expected front-end analysis result | `@api-verification-engineer` | 53, 54 |
| 56 | `tests/fixtures/platform/frontend/holdout.yaml` | Create | Front-end contract-drift/accessibility unresolved case | `@api-test-strategist` | 53, 54 |
| 57 | `docs/architecture/API_FORGE_PLATFORM_COMPLETION.md` | Create | Architecture, boundaries, waves and release gates | `@api-architecture-reviewer` | 1–24 |
| 58 | `docs/capabilities/API_FORGE_CAPABILITY_MATRIX.md` | Create | Human-readable capability states, limits and verifiers | `@api-dx-docs-reviewer` | 9–11, 33–56 |
| 59 | `docs/agents/AGENT_OUTPUT_CONTRACT.md` | Create | Agent recommendation/evidence/uncertainty contract | `@api-agentic-orchestrator` | 12, 13, 25, 26 |
| 60 | `docs/contracts/CapabilityRecord-v1.md` | Create | Public schema documentation | `@api-contract-architect` | 5, 7 |
| 61 | `docs/contracts/CapabilityRequest-v1.md` | Create | Surface request schema documentation | `@api-contract-architect` | 5, 22 |
| 62 | `docs/contracts/CapabilityResult-v1.md` | Create | Surface result and error schema documentation | `@api-contract-architect` | 5, 22 |
| 63 | `src/apiforge/application/artifacts.py` | Create | Shared official findings-envelope loader | `@api-contract-architect` | 1, 2 |
| 64 | `src/apiforge/rules/playbooks.yaml` | Modify | Register the completion reviewer coordinator profile | `@api-agentic-orchestrator` | 25 |
| 65 | `docs/contracts/VerticalCoverage-v1.md` | Create | Vertical fixture/golden/holdout schema documentation | `@api-verification-engineer` | 33, 34 |

**Total Files:** 65

The manifest deliberately does not list provider SDK modules or live UI
deployables. They are separate implementation units after the gateway has
proved read-only behavior and the capability matrix has a verifier for the
provider. This is a boundary, not a dropped requirement.

---

## Agent Assignment Rationale

Agents were discovered from the project-local `agents/**/*.md` fleet and the
project `.agents/skills/` mirrors. The architecture phase also ran the
deterministic route for the current case: phase `architecture`, dominant area
`CONTRACT`, recommended agent `api-contract-architect`, with all findings
mapped. The assignments are based on the file's responsibility, not on a
generic “AI agent” label.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| `@api-contract-architect` | 1, 2, 5, 6, 7, 35, 36, 60–62 | Owns contract shape, envelopes, compatibility and public schemas. |
| `@api-agentic-orchestrator` | 3, 4, 12, 13, 22, 59 | Owns bounded runtime, handoffs, policy-facing orchestration and parity. |
| `@api-platform-selector` | 8, 9, 11 | Owns evidence-based capability and architecture selection. |
| `@api-verification-engineer` | 10, 25, 34, 37, 41, 45, 48, 51, 55 | Verifies independently, preserves proof axes and rejects stale or incomplete evidence. |
| `@api-vendor-integration-engineer` | 14, 15, 16 | Owns provider-neutral adapters and capability declarations. |
| `@api-operations-engineer` | 17, 47 | Owns runbooks, CI/CD posture, receipts and operational gates. |
| `@aws-api-infra-reviewer` | 18 | Owns cloud posture interpretation from declared or collected offline artifacts. |
| `@api-data-access-architect` | 19, 39, 40 | Owns database access patterns and their unresolved evidence boundary. |
| `@api-event-driven-architect` | 20, 43, 44 | Owns broker/topic/consumer semantics and messaging limitations. |
| `@api-dx-docs-reviewer` | 23, 24, 53, 54, 58 | Owns consumer-facing surfaces, examples and documentation quality. |
| `@api-test-strategist` | 27–33, 38, 42, 46, 49, 52, 56 | Designs negative space, holdouts, smoke tests and mutation boundaries. |
| `@terraform-reviewer` | 50 | Reads Terraform statically and keeps unresolved variables explicit. |
| `@api-architecture-reviewer` | 57 | Reviews cross-vertical boundaries and deployment-safe architecture. |
| `@api-forge-verification` | 26 | Project skill teaches the verification workflow and evidence requirements. |
| `(general)` | 21 | Package marker only; no domain decision is delegated to a generic agent. |

**Agent Discovery:**
- Scanned: `E:/projetos/api-forge/agents/**/*.md` and
  `E:/projetos/api-forge/.agents/skills/**/SKILL.md`.
- Matched by: file type, rule areas, adapter boundary, KB domain and stated
  executor responsibilities.
- Guardrail: every assigned agent must emit a contract-shaped artifact; no
  assignment grants permission to mutate external systems.

---

## Code Patterns

### Pattern 1: Governed artifact envelope loader

```python
from pathlib import Path
from typing import Any
import json

from apiforge.contracts.base import ContractError
from apiforge.core.models import Finding


def load_findings_artifact(path: Path) -> tuple[Finding, ...]:
    """Read the official envelope without hiding malformed findings."""
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("AF-FINDINGS-INPUT", f"{path}: {exc}") from exc
    if isinstance(raw, dict):
        raw = raw.get("findings")
    if not isinstance(raw, list):
        raise ContractError("AF-FINDINGS-ENVELOPE", "expected findings list or {findings: list}")
    try:
        return tuple(Finding.model_validate(item) for item in raw)
    except Exception as exc:
        raise ContractError("AF-FINDINGS-CONTRACT", f"invalid finding: {exc}") from exc
```

This loader is used by CLI, MCP and dispatch. It never turns an invalid
payload into an empty list.

### Pattern 2: Safe static traversal

```python
binding = bindings.get(key)
if binding is None:
    diagnostics.append(
        _diag(
            "AF-FASTAPI-UNRESOLVED-BINDING",
            f"binding {key[0]!r}.{key[1]!r} is not present in the static index",
            scan.rel,
            scan.sha256,
            line,
        )
    )
    return
```

Resolvers return `None` for unknown symbols; traversals guard before indexing.
Only literal facts are emitted, and the unresolved branch is preserved in the
diagnostic stream.

### Pattern 3: Grounded agent artifact

```python
artifact = AgentArtifact(
    artifact_id=artifact_id,
    run_id=run_id,
    invocation_id=invocation_id,
    agent=agent_name,
    capability=capability,
    kind=ArtifactKind.SPECIALIST,
    schema_name="AgentArtifact/v1",
    payload={"recommendation": recommendation},
    evidence=tuple(fact_ids),
    assumptions=tuple(assumptions),
    risks=tuple(risks),
    unresolved=tuple(unresolved),
    confidence=confidence,
    content_sha256=content_sha256,
)
```

The guardrail checks that each evidence reference is present in the case or a
declared external receipt, that unsupported claims are named as unresolved,
and that an agent cannot promote its own recommendation to acceptance.

### Pattern 4: Capability matrix record

```yaml
capabilities:
  api.analyze:
    vertical: api
    state: supported
    surfaces: [cli, mcp, ide, ui]
    evidence: [case_manifest, facts, findings, smoke_test]
    limitations:
      - "static adapters do not execute application code"
    prerequisites: ["OpenAPI 3.1 contract", "supported project adapter"]
    risk: read_only
    rollback: "delete generated local case only"
    verifier: tests/e2e/test_platform_completion.py::test_platform_chain
```

Registry validation rejects records without state, limitations, verifier or a
declared evidence boundary. External provider entries start as `unsupported`
or `unresolved` until their own proof is registered.

### Pattern 5: External mutation gate

```text
request → capability lookup → risk classification → policy decision
       → [read/plan] or [approval gate + rollback + receipt] → verify
```

An adapter may return a plan without applying it. Apply is not reachable from
an agent's prose; it requires an explicit policy decision and a recorded gate.

---

## Data Flow

```text
1. Surface receives intent, project paths, contract paths and requested phase.
   │  validates CapabilityRequest/v1 and assigns a correlation id
   ▼
2. Case loader verifies input paths, existing hashes and the persisted case.
   │  malformed artifacts become AF-* governed errors
   ▼
3. Static extractor builds facts/IR and diagnostics.
   │  missing bindings and dynamic constructs remain unresolved
   ▼
4. Judge and next-step consume canonical findings and capability metadata.
   │  specialist selection is deterministic; recommendations cite evidence
   ▼
5. Supervisor invokes bounded agents through the model adapter.
   │  guardrails validate AgentArtifact/v1; policy blocks unsafe tools
   ▼
6. Graph builder derives provenance nodes/edges from persisted artifacts.
   │  evidence emitter verifies manifest hashes and policy digest
   ▼
7. OutcomeBrief renders DONE, REVIEW, DECIDE, BLOCKED or FAILED.
   │  DONE is refused while mandatory proof, gaps or independent checks remain
   ▼
8. CLI, MCP, IDE and UI project the same CapabilityResult/v1.
```

The critical smoke test must execute the chain from a fresh temporary case and
assert both the positive artifacts and the negative properties: no raw
traceback, no missing hash, no ungoverned external call, and no `DONE` without
independent proof.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Local filesystem and Git worktree | Read files, hashes, diff and patch plan | None for read; host policy for patch |
| CI/CD providers | Read pipeline definitions and reports; plan rerun/deploy | Provider credential broker, read-only default |
| IDEs | JSON-RPC/stdio projection of canonical requests/results | Host process boundary; no provider credential in core |
| Visual UI | Contract-driven local/API projection | Session auth handled by the UI host; action still policy-gated |
| Cloud posture | Read declared IaC, exported dumps and receipts | Offline artifacts; optional read-only adapter credentials |
| Databases | Read schema, migrations and static access patterns | Offline files or read-only connection adapter |
| Messaging brokers | Read topology/configuration/reports | Offline files or read-only adapter |
| Observability vendors | Read-only snapshots and intents | Existing provider-specific adapter policy |
| Model providers | `ModelAdapter` protocol only | Runtime-owned secret; never imported by deterministic core |

The gateway exposes `read`, `plan`, `apply` and `verify` as distinct phases.
Only `read` is enabled by default. A provider adapter may be installed without
being `supported`; the matrix records exactly what has been verified.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | FastAPI missing binding, envelope loader, registry validation, guardrails | `tests/adapters/test_fastapi_extractor.py`, `tests/runtime/test_supervisor.py` | Pytest, Pydantic | Every new branch has positive and negative assertions |
| Contract | Capability/request/result schemas and documented JSON shapes | `tests/contracts/`, `tests/mcp/test_tools.py`, `tests/dispatch/test_runner.py` | Pydantic JSON schema, pytest | No surface-specific shape drift |
| Integration | Case → graph/evidence/brief and adapter policy boundary | `tests/e2e/test_platform_completion.py` | Pytest, temp paths, fake adapter | Critical chain and policy refusal |
| E2E smoke | `analyze → next-step → graph → evidence → brief` | `tests/e2e/test_platform_completion.py` | CLI runner, local fake inputs | Every step produces the next official artifact |
| Parity | CLI, MCP, dispatch, IDE and UI projection from one request | `tests/dispatch/test_runner.py`, `tests/mcp/test_tools.py` | Shared fixtures | Equal canonical result; presentation may differ |
| Vertical lab | API, database, messaging, CI/CD, cloud and front-end | `tests/labs/test_platform_verticals.py` | Pytest, YAML manifest | Each vertical has fixture, golden and holdout |
| Golden | Stable expected recommendations/findings for representative fixtures | `tests/fixtures/platform/**/golden.json` | Deterministic fake adapter | Byte/hash-stable output except declared timestamps |
| Holdout | Unseen/unresolved/negative inputs | `tests/fixtures/platform/**/holdout.yaml` | Pytest, mutation probes | No invented fact; explicit unresolved or refusal |
| Mutation | Remove evidence, alter hashes, request external mutation | `tests/e2e/test_platform_completion.py`, `tests/runtime/test_supervisor.py` | Pytest, existing verification service | Gate blocks or names the exact gap |
| Static quality | Core source and test quality | Existing CI commands | Ruff, mypy, release check, SDD check | Core gates clean; vendor/scripts status separated |

Acceptance mapping:

- `AT-001` and `AT-004`: extractor regression plus CLI governed-error tests.
- `AT-002`: official envelope tests through CLI, MCP and dispatch.
- `AT-003`: end-to-end smoke test with receipts and graph hashes.
- `AT-005`: capability registry verifier and documentation link checks.
- `AT-006`: vertical lab manifest and six fixture/golden/holdout cells.
- `AT-007` and `AT-008`: agent guardrails, holdouts and architectural
  recommendation assertions.
- `AT-009`: integration gateway mutation refusal and approval-gate tests.
- `AT-010`: canonical surface projection parity tests.
- `AT-011`: stale hash and SDD/release evidence checks.

The lab distinguishes three outcomes: a passing proof, an explicit
`unsupported`/`unresolved` limitation, and a failure of the matrix itself.
An empty cell is never treated as coverage.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Missing or malformed findings file | Raise `AF-FINDINGS-INPUT`, `AF-FINDINGS-ENVELOPE` or `AF-FINDINGS-CONTRACT`; CLI returns governed JSON and non-zero status | No; fix input |
| Missing FastAPI binding | Emit `AF-FASTAPI-UNRESOLVED-BINDING` diagnostic and continue independent branches | No |
| Dynamic route, prefix or import | Emit existing unresolved diagnostic with source and limitation | No |
| Invalid case manifest or hash mismatch | Refuse graph/evidence; emit case integrity code and preserve no partial proof | No |
| Missing optional external tool | Return `unsupported` or `unresolved` with prerequisite and verifier | No; optional bounded discovery only |
| Agent schema/evidence violation | Reject artifact, record invocation failure and unresolved gap; do not accept recommendation | Bounded adapter retry only when policy allows |
| Conflicting specialist recommendations | Persist a `DecisionRecord` with dissent and send to referee or supervision | No automatic promotion |
| External action without policy/approval/rollback | Refuse or park in approval gate; no provider call | No |
| Provider timeout or transient read error | Return adapter receipt with failed status and source error; never infer result | Bounded retry only for declared read-safe adapters |
| Unexpected exception at CLI boundary | Map to `AF-CLI-INTERNAL` with correlation id; show traceback only in explicit debug mode and retain it as governed diagnostic | No automatic retry |

The error boundary must catch known `ContractError`, `AnalysisError`,
`DispatchError`, `CaseIntegrityError`, adapter errors and JSON/YAML input
errors. A final defensive boundary prevents raw tracebacks from normal CLI
entrypoints, but does not hide the error code, operation, source or unresolved
status.

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `APIFORGE_CAPABILITY_MATRIX` | path | packaged `rules/capability_matrix.yaml` | Matrix loaded and validated before public capability output |
| `APIFORGE_CASE_DIR` | path | `.apiforge` | Root for cases, receipts, graphs and runtime artifacts |
| `APIFORGE_EXTERNAL_MODE` | enum | `read_only` | `read_only`, `plan_only` or policy-controlled `apply` |
| `APIFORGE_AGENT_POLICY` | path | existing policy loader | Budgets, tool allowlist, approval gates and mutation rules |
| `APIFORGE_DEBUG_TRACEBACK` | bool | `false` | Enables a governed debug diagnostic, never a normal uncontrolled traceback |
| `APIFORGE_DETAIL_LEVEL` | enum | `normal` | Output projection level; never removes critical evidence |
| `APIFORGE_INTEGRATION_ALLOWLIST` | list | empty | Explicit adapter names available to a run |
| `APIFORGE_EVIDENCE_FRESHNESS` | enum | `strict` | Recompute, reject stale evidence or record visible unresolved state |

Configuration is parsed before adapter discovery. Secrets are references to a
host credential broker and never persisted in case artifacts, prompts or
golden files.

---

## Security Considerations

- Keep the deterministic core free of model, cloud, database and broker SDKs;
  all external access uses a declared adapter and policy gate.
- Treat repository files, contract descriptions and agent outputs as
  untrusted input. Validate Pydantic shapes, reject unknown fields where the
  contract requires it, and never execute analyzed source code.
- Use input, tool, retrieval and output rails: allowlist tool names and paths,
  validate arguments before invocation, isolate sandbox writes, and validate
  agent output after invocation.
- Redact secrets and sensitive values from prompts, receipts, logs and UI
  projections. Case artifacts contain hashes and provenance, not credentials.
- Require least privilege and read-only credentials for Git, CI/CD, cloud,
  database, broker and vendor adapters. A plan is not an apply.
- Require approval, rollback and receipt for external mutation; destructive or
  irreversible operations remain unavailable unless an explicit human policy
  enables them.
- Prevent path traversal, symlink escape, artifact overwrite and case/input
  overlap using the existing case storage protections.
- Make prompt-injection resistance an adapter concern: external text can
  inform a finding but cannot change policy, tool allowlists or task scope.
- Keep security findings, failed checks, unresolved claims and unavailable
  scanners visible; do not reduce them to a clean summary to save context.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured event records with correlation id, case id, run id, operation, status, `AF-*` code and redaction metadata |
| Metrics | Counts and rates for governed command outcomes, unresolved states, stale evidence, capability verification, adapter failures, parity drift and holdout results; thresholds are configured and evidence-backed |
| Tracing | Optional OpenTelemetry projection at the surface, supervisor, adapter and verifier boundaries; trace context never replaces artifact provenance |
| Audit | Existing autonomy ledger, policy decision, approval gate, adapter receipt and immutable case artifacts |
| Health | Capability registry load, contract registry load and optional adapter discovery reported as explicit capability states |
| Debugging | Detailed tracebacks only behind `APIFORGE_DEBUG_TRACEBACK`; normal output contains stable code and governed context |

No metric is presented as a performance or reliability fact unless its source,
time window and measurement artifact are present. A missing telemetry tool is a
visible limitation, not a zero.

---

## Pipeline Architecture (if applicable)

The feature has an evidence and evaluation pipeline even when no production
ETL is involved. The pipeline is offline-first and append-oriented.

### DAG Diagram

```text
[source files/contracts/dumps]
              │ hash + inventory
              ▼
       [raw case artifacts]
              │ validate + normalize
              ▼
        [facts + diagnostics]
              │ rules + IR composition
              ▼
        [findings + decisions]
              │ specialist recommendation / guardrail
              ▼
        [agent artifacts + tasks]
              │ independent verification
              ├──────────────→ [golden/holdout results]
              ▼
   [receipt + provenance graph]
              │ render
              ▼
        [OutcomeBrief + projections]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|-------------|-------------|-----------|
| Case artifacts | `case_id/artifact_kind` | Per case/run | Keeps immutable inputs and derived artifacts isolated |
| Agent artifacts | `run_id/invocation_id` | Per invocation | Supports replay, audit and bounded retention |
| Evidence receipts | `case_id/receipt_kind` | Per verification run | Prevents a newer receipt from overwriting history |
| Lab results | `vertical/case_kind/run_id` | Per lab execution | Allows golden, holdout and mutation results to be compared |
| Integration receipts | `adapter/operation_id` | Per adapter operation | Separates read, plan, apply and verify outcomes |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Case analysis | Recompute only when input hashes or analyzer version change | Input SHA-256 + generator | None; explicit invalidation |
| Graph export | Rebuild from changed case artifacts | Artifact digest | None |
| Evidence receipt | Re-emit on current manifest/policy digest | Case + policy digest | None |
| Capability verification | Re-run changed capability or dependency cells | Capability id + source hashes | None |
| Lab matrix | Execute changed vertical/case and mandatory smoke set | Fixture/golden/holdout hashes | None |

No time-based lookback is inferred for static analysis. External evidence must
declare its timestamp and source; freshness policy decides whether it can be
used.

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| New capability field | Add optional field, update registry/docs/verifier, then require it in the next contract version | Keep `CapabilityRecord/v1` projection |
| New capability state | Reject unknown states until contract and all surfaces are updated | Preserve previous state and mark new provider unresolved |
| Findings envelope change | Accept both only through the boundary loader with explicit compatibility test | Keep official envelope as source of truth |
| Contract breaking change | Add `v2`, retain `v1` projection for existing surfaces and receipts | Roll back surface adapter to `v1` |
| New vertical | Add fixture/golden/holdout, matrix cell, docs and verifier before public promotion | Leave state `unsupported` |
| Provider adapter change | Recompute source hash and independent receipt | Disable adapter and retain old receipt |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Artifact schema | Pydantic contract registry | Every emitted artifact validates | Block next stage and emit contract code |
| Hash integrity | Case/evidence services | Every declared artifact matches its SHA-256 | Refuse graph/evidence/brief proof |
| Finding provenance | Graph builder and verifier | Every finding has fact or explicit unresolved diagnostic | Keep REVIEW/BLOCKED; never promote |
| Capability completeness | Capability verifier | Every public record has docs, limits and verifier | Matrix check fails the release |
| Vertical coverage | Platform lab | Each required vertical has fixture, golden and holdout | Name missing cell and block completion |
| Surface parity | Shared projection tests | Same canonical request yields equivalent result | Block the divergent surface |
| Mutation safety | Policy/gate tests | No external mutation without approval/rollback/receipt | Refuse action |
| Lint/type quality | Ruff, mypy, SDD/release checks | Core gates pass; excluded scopes reported separately | Release remains review/block depending on gate |

---

## Implementation Phases

### Phase 0 — Restore the critical deterministic chain

- Patch FastAPI traversal guards and add missing-binding holdout.
- Add the canonical findings envelope loader and use it in CLI, MCP and
  dispatch.
- Add governed CLI error handling for all critical entrypoints.
- Prove `analyze → next-step → graph → evidence → brief` on a fresh case.
- Record updated SDD evidence and separate core, scripts/vendor and docs lint
  scopes.

Exit gate: `AT-001` through `AT-004` pass without a raw traceback.

### Phase 1 — Canonical capability and agent output contracts

- Add platform contracts, registry entries and matrix loader.
- Add capability verifier requiring documentation, limitations, evidence and
  verifier for every public record.
- Add runtime guardrails and update the supervisor to retain assumptions,
  risks, unresolved states and evidence references.
- Publish the agent output contract and completion-reviewer agent.

Exit gate: `AT-005`, `AT-007` and `AT-008` pass with fake adapter replay.

### Phase 2 — Six vertical proof cells

- Add representative example projects for APIs, databases, messaging, CI/CD,
  cloud and front-end.
- Add one golden and one holdout for each vertical and register them in the
  lab manifest.
- Implement the matrix verifier and mutation/negative cases.
- Keep provider-specific cells `unsupported` or `unresolved` until their own
  adapter evidence is available.

Exit gate: `AT-006` and the data quality gates pass; missing tools are visible.

### Phase 3 — Surfaces and controlled integrations

- Add canonical projections for CLI, MCP, IDE and UI.
- Add generic Git, CI/CD, cloud, data and messaging gateway protocols.
- Add read-only local/fake adapters and policy tests for plans and mutation
  refusal.
- Document how real provider adapters are added without importing provider SDKs
  into the core.

Exit gate: `AT-009` and `AT-010` pass for local/fake adapters. Live provider
support stays at the matrix state justified by evidence.

### Phase 4 — Independent completion and release evidence

- Re-run full focused tests, mypy, core Ruff and release checks.
- Run SDD check and regenerate evidence after every relevant source change.
- Run vertical holdouts and mutation probes independently of the producer.
- Build the Outcome Brief with unresolved gaps and no premature `DONE`.

Exit gate: `AT-011` passes and the handoff reports all remaining unresolved
items explicitly.

---

## Deployment Strategy

The first deployment target is the local/offline CLI and MCP package. The
contract registry, rules, capability matrix, agents, skills and fixture labs
ship with the package. IDE and UI components consume the same canonical
projection through a host process or local service; they are not imported into
the deterministic core.

CI/CD integration starts as read-only report ingestion and plan generation.
Cloud, database and messaging adapters start from exported artifacts or
read-only credentials. Promotion to a mutating environment is outside the
automatic build and requires the repository policy, approval gate, rollback
record and independent verification.

Release packaging must include:

- source and contract hashes;
- capability matrix and verifier result;
- vertical lab result with golden and holdout references;
- focused and full test results;
- Ruff, mypy, SDD and release-check evidence;
- explicit external-tool availability and unresolved gaps.

---

## Rollback Plan

1. Keep all work in a branch/worktree and preserve the previous contract
   projection until the new one has passed parity tests.
2. Disable a capability by moving its matrix state to `unsupported` or
   `unresolved` rather than deleting evidence or returning an optimistic
   result.
3. Disable an integration adapter through the allowlist/policy and retain its
   receipts for audit.
4. Revert the new surface projection independently if CLI/MCP/IDE/UI parity
   detects divergence; the core contracts and case artifacts remain readable.
5. If a contract needs rollback, serve the previous version and keep the new
   artifacts as rejected or incompatible records; never rewrite accepted
   historical evidence.
6. Re-run the focused chain and independent verifier after rollback. The
   system remains `REVIEW` or `BLOCKED` until current proof is available.

---

## Open Questions

These do not block the foundation build but must be resolved before declaring
provider or production surface support:

- Which concrete IDE protocol and host packaging should receive the first
  production bridge?
- Which UI runtime is appropriate for the visual projection without coupling
  it to the Python core?
- Which Git hosts, CI/CD systems, cloud providers, databases and brokers get
  the first read-only adapters?
- Which credential broker and tenant isolation policy will be used for external
  adapters?
- Which human review process accepts golden recommendations and changes them
  into durable ground truth?
- What resource/time budgets should be configured per provider capability?
- Which SDD evidence storage and retention policy is required for teams?

Until answered with evidence and a verifier, each affected capability remains
`unsupported` or `unresolved` and the gap is included in the Outcome Brief.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | design-agent | Initial design from approved DEFINE; foundation, six vertical proof cells, shared surfaces and governed integration gateway specified. |
| 1.1 | 2026-09-22 | ship-agent | Feature implementada, documentada e arquivada. |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_PLATFORM_COMPLETION/`
