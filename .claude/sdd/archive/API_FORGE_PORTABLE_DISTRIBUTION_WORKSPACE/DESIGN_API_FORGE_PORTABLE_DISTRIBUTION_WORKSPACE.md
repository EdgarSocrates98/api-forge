# DESIGN: API Forge Portable Distribution, Workspace and Host Activation

> Technical design for implementing API Forge as an installed, portable, host-agnostic engineering platform.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_PORTABLE_DISTRIBUTION_WORKSPACE |
| **Date** | 2026-09-24 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_PORTABLE_DISTRIBUTION_WORKSPACE.md](./DEFINE_API_FORGE_PORTABLE_DISTRIBUTION_WORKSPACE.md) |
| **Status** | ✅ Shipped |

The design confidence is **strong** for the selected architecture: the codebase already has versioned immutable contracts, canonical CLI/MCP projections, plan-only host activation, read-only evidence boundaries, context funneling and local test fixtures. The novel distribution/workspace combination is bounded by explicit contracts and must be validated with temporary filesystem fixtures before promotion.

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────┐
│                    INSTALLED API FORGE                               │
│  Python package + CLI + MCP stdio + optional TUI/Rich + assets       │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ importlib.resources / executable path
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         PATH + CONFIG                               │
│ APIFORGE_HOME · config · cache · package assets · capability doctor  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ current path + explicit overrides
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  ROOT AND MANIFEST RESOLUTION                        │
│ module → repository (.git) → project.yaml → parent workspace.yaml   │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ read-only scanners + declared refs
                               ▼
┌──────────────────────────────┴───────────────────────────────────────┐
│                    WORKSPACE GRAPH + EVIDENCE                         │
│ repository/service/contract/dependency/runtime IR                    │
│ observed · declared · inferred · heuristic · unresolved              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ scope + target + impact funnel
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     CANONICAL APPLICATION SERVICES                    │
│ portable status · doctor · inspect · init · context · activation     │
└───────────────┬──────────────────────┬───────────────────────────────┘
                │                      │
                ▼                      ▼
      CLI/TUI/Rich/JSON          MCP local stdio
                │                      │
                └──────────────┬───────┘
                               ▼
                 Host plans / generated adapters
                 explicit diff + source hash + approval
```

### Layering and dependency direction

```text
contracts → distribution paths/config/assets → workspace discovery/graph
          → context scopes/funnel → application facades
          → CLI, MCP, TUI, host projections
```

`contracts` remains pure and does not import CLI, host SDKs, network clients or
model SDKs. Distribution and workspace services read local state only. The
application layer composes services and applies policy. Surfaces render the
canonical application result and never add semantics. Host activation can emit
plans and diffs but cannot write host configuration implicitly.

There is one deployable unit: the installed Python package. MCP is an optional
local process over stdio, not a required network service. No shared dependency
is introduced between separate deployable units and no circular dependency is
allowed between contracts, services and surfaces.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Distribution paths | Resolve package resources, user-selected runtime root, config, cache and executable diagnostics | Python `pathlib`, `importlib.resources`, typed dataclasses |
| Configuration resolver | Merge defaults, explicit user config, workspace manifest, project manifest and CLI overrides | YAML, Pydantic validation, deterministic precedence |
| Asset registry | Load packaged agents, skills, knowledge, templates and host metadata without using the current working directory | Package data, manifest hash, read-only loader |
| Root discovery | Find current module, repository, project manifest and parent workspace manifest | Read-only filesystem/Git marker inspection |
| Project manifest | Store minimal project connection state and defaults | `ProjectManifest/v1`, frozen Pydantic contract |
| Workspace manifest | Register independent repositories and optional declared relationships | `WorkspaceManifest/v1`, frozen Pydantic contract |
| Workspace graph | Build repository/service/contract/dependency/runtime IR with provenance and unresolved edges | Existing graph contracts plus workspace extensions, JSONL artifacts |
| Context resolver | Select repo, workspace or target scope and apply impact/context funnel | Typed scope contract, existing funnel/economy ledger |
| Portable application facade | Expose `inspect`, `init`, `status`, `doctor`, `context`, workspace and host plan operations | `src/apiforge/application`, typed results |
| Host activation bridge | Negotiate capabilities and render small deterministic adapters or diffs | Existing `HostAdapter`/`ActivationPlan`, packaged templates |
| CLI surfaces | Register human-mode command groups while preserving expert verbs and aliases | Typer, existing CLI composition root |
| MCP surfaces | Mirror canonical application payloads over local stdio | Existing MCP tool registry and server |
| Documentation/contracts | Describe install modes, manifests, scopes, evidence, host limits and migration | Markdown contracts, README and guides |
| Verification matrix | Exercise prefixes, restricted environments, fixtures, projections and compatibility | pytest, temporary paths, golden/holdout/mutation fixtures |

---

## Key Decisions

### Decision 1: Installed package is the source of truth

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** The current operating model exposes source assets through repository
mirrors. That forces projects to carry knowledge and makes host integration look
like a runtime dependency.

**Choice:** Package API Forge assets under `src/apiforge/host_assets` and the
existing knowledge package. Resolve them through `importlib.resources`; consumer
repositories receive only minimal manifests and explicitly requested adapters.

**Rationale:** The package can be installed once by `uv`, `pipx`, a virtual
environment or an explicit prefix. The current directory is then only input
context, never the location from which the Forge loads its authority.

**Alternatives Rejected:**

1. Copy all skills and agents into every project — rejected because it duplicates
   source of truth and inflates project context.
2. Require repository checkout for execution — rejected because it fails the
   user-selected-prefix and restricted-environment requirements.

**Consequences:**

- Package-data inclusion and asset hashing become release gates.
- Existing mirrors need a generated-compatibility migration path.
- A missing package asset is a diagnosed installation error, not a silent fallback.

### Decision 2: Host integration is optional and hostless operation is first-class

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** Machines may lack a supported host, network access, credentials,
admin privileges or an MCP daemon.

**Choice:** All local discovery, context, SDD, graph, evidence, verification,
agents and skills are available through the installed Forge. Host activation and
MCP are additional surfaces. Local MCP uses stdio and does not require a port.

**Rationale:** The core can remain offline-first and useful in locked-down
environments. Missing external capabilities become structured `unresolved` or
`unavailable` states with an unlock, never a false success.

**Alternatives Rejected:**

1. Require Claude, Devin, Codex, Copilot or a remote MCP server — rejected because
   it makes optional host capabilities a product prerequisite.
2. Treat network failure as installation failure — rejected because local assets
   and read-only analysis do not require network access.

**Consequences:**

- `doctor` must distinguish installation, permissions, host, network and provider
  gaps.
- Design and tests must not infer production capability from local fixtures.

### Decision 3: User-selected paths are explicit, not guessed from the host

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** Users without admin rights may install into a writable directory,
virtual environment, mounted volume or container. Windows, WSL and POSIX use
different executable locations.

**Choice:** Use explicit environment/configuration overrides. `APIFORGE_HOME`
selects the user-owned runtime state/cache root; `APIFORGE_CONFIG` and
`APIFORGE_CACHE` may override individual locations. The installed package root
and executable path are reported by `doctor`, not inferred from the project cwd.

**Rationale:** Explicit paths are portable and auditable. The project state may
remain under the resolved project manifest while global/cache state can be moved
to a permitted location.

**Alternatives Rejected:**

1. Write into the installed package directory — rejected because package
   directories can be read-only and are not project state.
2. Assume a fixed OS home directory — rejected because enterprise, container and
   portable environments can redirect user state.

**Consequences:**

- Path values must be normalized, absolute and checked for writability.
- Documentation must show platform-specific executable path setup without
  requiring a global installer.

### Decision 4: Workspace is a virtual graph above independent repositories

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** Platform teams need cross-repository impact without forcing a
monorepo or rewriting Git metadata.

**Choice:** `workspace.yaml` registers repository roots and types. Discovery and
declared relationships produce a virtual graph. Each repository retains its own
`.git` and project manifest.

**Rationale:** The graph can combine observed local signals and explicit user
declarations while preserving repository boundaries and provenance.

**Alternatives Rejected:**

1. Require a parent Git repository — rejected because independent repositories are
   a stated requirement.
2. Infer every relationship from names or directory layout — rejected because
   heuristics must not become confirmed facts.

**Consequences:**

- Workspace graph IDs must be stable across invocation paths.
- Unsupported or ambiguous edges remain `inferred`, `heuristic` or `unresolved`.

### Decision 5: Canonical application results precede every surface

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** The repository already prevents CLI, MCP, Rich, JSON and TUI from
drifting by projecting shared experience contracts.

**Choice:** New distribution, workspace and context commands return typed
application results. CLI, MCP, TUI/Rich and host adapters project those results
without adding semantics.

**Rationale:** One source of truth makes compatibility, evidence and golden tests
possible across expert and human interfaces.

**Alternatives Rejected:**

1. Let each surface scan and resolve roots independently — rejected because it
   creates inconsistent scopes and evidence.
2. Make the TUI or MCP the authority — rejected because surfaces are optional.

**Consequences:**

- Every new command gets a canonical result contract and a projection test.
- Surface-specific formatting remains outside domain services.

### Decision 6: Host output is generated, diffable and approval-gated

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** Existing activation plans are plan-only and the project must not
overwrite user-owned host files automatically.

**Choice:** Store host templates and source hashes in the installed Forge. Render
small adapters, manifests or diffs only on request. Sync defaults to preview and
refuses conflicting overwrites until an explicit policy/approval path exists.

**Rationale:** This preserves portability without hiding a mutation boundary.

**Alternatives Rejected:**

1. Automatic `sync` overwrite — rejected because it can destroy user edits.
2. Symlink by default — rejected because it is unreliable across Windows,
   containers, WSL, Git and remote workspaces.

**Consequences:**

- Host artifacts must carry generator identity, source hash and limitations.
- Conflict and refusal codes must be added to `docs/catalog-contract.md` before
  implementation is shipped.

### Decision 7: Evidence level is part of every workspace claim

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-24 |

**Context:** The project contract distinguishes observed, declared, inferred,
heuristic, verified and unresolved states.

**Choice:** Every graph node, edge, scope result and doctor capability carries
evidence references and limitations. A missing or stale input is retained as an
unresolved diagnostic.

**Rationale:** Impact context is useful only if an agent can tell what was seen,
what was declared and what remains a hypothesis.

**Alternatives Rejected:**

1. Boolean `confirmed` graph edges — rejected because it suppresses extraction
   uncertainty.
2. Treat local fixtures as production proof — rejected by the project protocol.

**Consequences:**

- Graph and context payloads are slightly larger but remain auditable.
- Context compaction must preserve codes, hashes, evidence and unresolved state.

---

## File Manifest

Every planned build file has an assigned specialist. Existing files marked
`Modify` must preserve current expert behavior and add compatibility tests.

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `pyproject.toml` | Modify | Add `all` package extras and package-data inclusion for portable assets | @shell-script-specialist | 21-26 |
| 2 | `src/apiforge/contracts/distribution.py` | Create | Versioned install/path/doctor contracts | @schema-designer | None |
| 3 | `src/apiforge/contracts/workspace.py` | Create | Project and workspace manifest contracts, repository refs and graph claims | @schema-designer | 5 |
| 4 | `src/apiforge/contracts/context.py` | Create | Scope, target, funnel and context result contracts | @schema-designer | 2, 3 |
| 5 | `src/apiforge/contracts/graph.py` | Modify | Add closed workspace node/edge vocabulary without breaking existing graph payloads | @schema-designer | 3 |
| 6 | `src/apiforge/contracts/host.py` | Modify | Extend host capability/activation metadata with generated asset provenance | @schema-designer | 2, 21-26 |
| 7 | `src/apiforge/distribution/__init__.py` | Create | Public distribution package boundary | @python-developer | 2 |
| 8 | `src/apiforge/distribution/paths.py` | Create | Resolve package root, `APIFORGE_HOME`, config, cache and executable diagnostics | @python-developer | 2 |
| 9 | `src/apiforge/distribution/config.py` | Create | Deterministic defaults/global/workspace/project/CLI precedence | @python-developer | 2, 3, 8 |
| 10 | `src/apiforge/distribution/assets.py` | Create | Load and hash package-owned agents, skills, knowledge and templates | @python-developer | 1, 21-26 |
| 11 | `src/apiforge/distribution/doctor.py` | Create | Diagnose installation, permissions, paths, host, network and optional capabilities | @code-reviewer | 2, 8-10 |
| 12 | `src/apiforge/workspace/__init__.py` | Create | Public workspace package boundary | @python-developer | 3 |
| 13 | `src/apiforge/workspace/discovery.py` | Create | Find module, repository, project and parent workspace roots | @codebase-explorer | 3, 8 |
| 14 | `src/apiforge/workspace/manifests.py` | Create | Read/write minimal YAML manifests through versioned contracts | @python-developer | 3, 9, 13 |
| 15 | `src/apiforge/workspace/graph.py` | Create | Build virtual graph from read-only facts and declarations | @genai-architect | 3-5, 13-14 |
| 16 | `src/apiforge/workspace/service.py` | Create | Compose discovery, manifests, graph and workspace status | @python-developer | 12-15 |
| 17 | `src/apiforge/context/__init__.py` | Create | Public context package boundary | @python-developer | 4 |
| 18 | `src/apiforge/context/resolver.py` | Create | Resolve scope, target, root and impact inputs | @genai-architect | 4, 13-16 |
| 19 | `src/apiforge/context/scopes.py` | Create | Closed repo/workspace/target scope selection and validation | @schema-designer | 4, 18 |
| 20 | `src/apiforge/context/service.py` | Create | Apply graph impact and existing context funnel to canonical context output | @genai-architect | 15, 18-19, existing `application/funnel.py` |
| 21 | `src/apiforge/host_assets/__init__.py` | Create | Package data boundary for host assets | @python-developer | 1 |
| 22 | `src/apiforge/host_assets/manifest.yaml` | Create | Asset registry, source hashes, host capability metadata and versions | @schema-designer | 6, 21 |
| 23 | `src/apiforge/host_assets/loader.py` | Create | Read-only package-resource loader and hash verifier | @python-developer | 10, 21-22 |
| 24 | `src/apiforge/host_assets/templates/CLAUDE.md.tmpl` | Create | Minimal generated Claude adapter template | @code-documenter | 22 |
| 25 | `src/apiforge/host_assets/templates/AGENTS.md.tmpl` | Create | Minimal generated Codex/Devin/Copilot instruction template | @code-documenter | 22 |
| 26 | `src/apiforge/host_assets/templates/mcp_config.json.tmpl` | Create | Optional local MCP registration template | @code-documenter | 22 |
| 27 | `src/apiforge/agentops/hosts.py` | Modify | Point host declarations at package-owned assets and explicit capabilities | @genai-architect | 6, 22 |
| 28 | `src/apiforge/agentops/activation.py` | Modify | Produce portable plan/diff/source-hash activation results | @code-reviewer | 6, 22-26 |
| 29 | `src/apiforge/dispatch/mirrors.py` | Modify | Convert mirror publication to generated, provenance-labelled compatibility output | @code-reviewer | 22-28 |
| 30 | `src/apiforge/knowledge/loader.py` | Modify | Resolve bundled and cache-backed knowledge without cwd coupling | @python-developer | 8-10, 23 |
| 31 | `src/apiforge/application/portable.py` | Create | Canonical `inspect`, `init`, `status` and `doctor` facade | @python-developer | 7-11, 16 |
| 32 | `src/apiforge/application/workspace.py` | Create | Canonical workspace discovery/add/status facade | @python-developer | 16 |
| 33 | `src/apiforge/application/context.py` | Create | Canonical scoped context/impact facade | @genai-architect | 18-20, existing funnel/graph services |
| 34 | `src/apiforge/application/experience_projection.py` | Modify | Project portable/workspace results across JSON, Rich and TUI | @genai-architect | 31-33, existing experience contracts |
| 35 | `src/apiforge/cli_distribution.py` | Create | Human and expert CLI commands for install context, inspect and doctor | @python-developer | 31, 34 |
| 36 | `src/apiforge/cli_workspace.py` | Create | `workspace discover|add|status` and scope options | @python-developer | 32, 34 |
| 37 | `src/apiforge/cli_context.py` | Create | `context` and target/scope output modes | @python-developer | 33, 34 |
| 38 | `src/apiforge/cli.py` | Modify | Register new command groups while preserving legacy aliases and exit contracts | @python-developer | 35-37 |
| 39 | `src/apiforge/mcp/tools.py` | Modify | Mirror portable/workspace/context application payloads over MCP | @python-developer | 31-34 |
| 40 | `src/apiforge/mcp/server.py` | Modify | Register new read/compose tools without changing local transport defaults | @python-developer | 39 |
| 41 | `docs/catalog-contract.md` | Modify | Catalog new path, manifest, workspace, host-conflict and capability refusal codes | @code-documenter | 2-6, 8-11, 22-29 |
| 42 | `docs/contracts/Distribution-v1.md` | Create | Installation paths, asset provenance and doctor contract | @code-documenter | 2, 8-11 |
| 43 | `docs/contracts/ProjectManifest-v1.md` | Create | Minimal repository manifest contract | @code-documenter | 3, 14 |
| 44 | `docs/contracts/WorkspaceManifest-v1.md` | Create | Independent repository workspace contract | @code-documenter | 3, 14-16 |
| 45 | `docs/contracts/ArchitectureGraph-v1.md` | Create | Graph nodes, edges, evidence and unresolved semantics | @code-documenter | 3-5, 15 |
| 46 | `docs/contracts/ContextScope-v1.md` | Create | Repo/workspace/target scope and context funnel contract | @code-documenter | 4, 18-20 |
| 47 | `docs/guides/API_FORGE_PORTABLE_DISTRIBUTION.md` | Create | Installation, restricted environments, root discovery and workspace guide | @code-documenter | 8-20, 31-38 |
| 48 | `docs/guides/API_FORGE_PLATFORM_USAGE.md` | Modify | Add hostless human-mode and portable installation usage | @code-documenter | 31-40 |
| 49 | `docs/guides/API_FORGE_EXPERIENCE_INTEROPERABILITY.md` | Modify | Explain canonical projections, host activation and capability limits | @code-documenter | 27-40 |
| 50 | `docs/HOST_PARITY.md` | Modify | Separate declared parity, observed capability and generated adapters | @code-documenter | 6, 27-29 |
| 51 | `docs/API_FORGE_EVOLUTION_MAP.md` | Modify | Track implementation wave and post-ship deferred brainstorm items | @code-documenter | 47-50 |
| 52 | `README.md` | Modify | Document install extras, `init`, `inspect`, `status`, `doctor`, `context`, workspace, MCP and offline operation | @code-documenter | 35-40, 47-51 |
| 53 | `tests/contracts/test_distribution.py` | Create | Contract validation and version/extra rejection cases | @test-generator | 2 |
| 54 | `tests/contracts/test_workspace.py` | Create | Manifest and graph contract validation | @test-generator | 3, 5 |
| 55 | `tests/contracts/test_context.py` | Create | Scope and context result validation | @test-generator | 4 |
| 56 | `tests/distribution/test_paths.py` | Create | Prefix, env override, read-only and platform path behavior | @test-generator | 8 |
| 57 | `tests/distribution/test_assets.py` | Create | Package-resource loading, hashes and missing asset diagnostics | @test-generator | 10, 21-23 |
| 58 | `tests/distribution/test_doctor.py` | Create | Restricted environment and optional capability diagnostics | @test-generator | 11, 31 |
| 59 | `tests/workspace/test_discovery.py` | Create | Nested roots, sibling repos and explicit root overrides | @test-generator | 13-14 |
| 60 | `tests/workspace/test_graph.py` | Create | Observed/declared/inferred/unresolved graph edges and stable IDs | @test-generator | 15 |
| 61 | `tests/workspace/test_service.py` | Create | Workspace init/add/status integration with temp repositories | @test-generator | 16 |
| 62 | `tests/context/test_resolver.py` | Create | Scope and target selection from nested paths | @test-generator | 18-20 |
| 63 | `tests/context/test_scopes.py` | Create | Invalid scope/target and impact narrowing cases | @test-generator | 19-20 |
| 64 | `tests/host_assets/test_render.py` | Create | Deterministic templates, source hashes and conflict previews | @test-generator | 22-29 |
| 65 | `tests/agentops/test_hosts.py` | Modify | Package asset and capability declarations for all current hosts | @test-generator | 27 |
| 66 | `tests/agentops/test_activation.py` | Modify | Plan-only activation and no-overwrite guarantees | @test-generator | 28-29 |
| 67 | `tests/mcp/test_tools.py` | Modify | CLI/MCP payload parity for portable surfaces | @test-generator | 39-40 |
| 68 | `tests/application/test_experience_parity.py` | Modify | Canonical projection parity across JSON, Rich and TUI | @test-generator | 34 |
| 69 | `tests/e2e/test_portable_distribution.py` | Create | Install-prefix, hostless and blocked-network vertical slice | @test-generator | 1, 8-11, 31, 35-40 |
| 70 | `tests/e2e/test_workspace_context.py` | Create | Independent repositories, graph and targeted context vertical slice | @test-generator | 13-20, 32-33 |
| 71 | `tests/fixtures/portable_distribution/project.yaml` | Create | Minimal consumer project fixture | @test-generator | 3, 14 |
| 72 | `tests/fixtures/portable_distribution/config.yaml` | Create | Explicit path/config precedence fixture | @test-generator | 9 |
| 73 | `tests/fixtures/portable_distribution/expected_doctor.json` | Create | Canonical restricted-environment doctor output | @test-generator | 11, 58 |
| 74 | `tests/fixtures/workspaces/workspace.yaml` | Create | Independent repository workspace fixture | @test-generator | 3, 14-16 |
| 75 | `tests/fixtures/workspaces/expected_graph.json` | Create | Evidence-labelled graph and unresolved-edge golden fixture | @test-generator | 15, 60 |

**Total Files:** 75 planned entries

---

## Agent Assignment Rationale

> Agents discovered from the Agentspec agent catalog and matched by file type,
> purpose, KB domain and existing project boundaries.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @schema-designer | 2-6, 14, 19, 22, 43-46 | Versioned closed contracts, manifest schemas, graph vocabulary and evidence fields |
| @python-developer | 7-10, 12, 14, 16-18, 23, 30-32, 35-40 | Python package boundaries, path/config services, parsers, facades and CLI/MCP composition |
| @genai-architect | 15, 18, 20, 27, 33-34 | Deterministic context routing, impact graph, hostless agent surfaces and canonical projections |
| @codebase-explorer | 13 | Repository/workspace root discovery must reuse existing scanner conventions and remain read-only |
| @shell-script-specialist | 1 | Package extras, wheel data inclusion and executable/prefix behavior cross shell and packaging boundaries |
| @code-reviewer | 11, 28-29 | Permission, overwrite, asset provenance and refusal boundary review |
| @code-documenter | 24-26, 41-52 | Public install, host, contract, migration and troubleshooting documentation |
| @test-generator | 53-75 | Pytest fixtures, integration/e2e coverage, golden/holdout and projection parity |

**Agent Discovery:**

- Scanned: `C:\Users\edgar\.codex\plugins\cache\agentspec\agentspec\3.6.0\agents/**/*.md`
- Matched by: file type, purpose keywords, path patterns, KB domains and project conventions.
- No data-engineering pipeline specialist is needed because the DEFINE explicitly marks IaC/data-pipeline context as not applicable.

---

## Code Patterns

### Pattern 1: Frozen versioned manifest

Use the existing `VersionedContract` base and Pydantic closed models for every
persisted manifest. This follows the KB patterns for typed validation and the
project convention that v2 is additive rather than an in-place mutation.

```python
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract


class ProjectManifest(VersionedContract):
    """Minimal project connection state; no knowledge or secret values."""

    schema: Literal["apiforge/project/v1"] = "apiforge/project/v1"
    project_id: str
    root: str
    workspace_id: str | None = None
    default_scope: Literal["repo", "workspace", "target"] = "repo"
    target: str | None = None
    hosts: tuple[str, ...] = Field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple)
```

`extra="forbid"`, frozen values and a literal schema prevent silent acceptance
of unsupported configuration. Paths are normalized before model construction;
secrets and credentials are rejected from the manifest contract.

### Pattern 2: Explicit path resolution with no cwd asset coupling

Use a pure resolver with environment/config inputs. The package root is obtained
from package resources; writable runtime state is separate and user-selected.

```python
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class ForgePaths:
    package_root: Path
    state_root: Path
    config_path: Path | None
    cache_root: Path


def resolve_paths(*, cwd: Path, package_root: Path, env: Mapping[str, str]) -> ForgePaths:
    project_state = cwd / ".apiforge"
    state_root = (
        Path(env["APIFORGE_HOME"]).expanduser() if env.get("APIFORGE_HOME") else project_state
    )
    config_path = Path(env["APIFORGE_CONFIG"]).expanduser() if env.get("APIFORGE_CONFIG") else None
    cache_root = (
        Path(env["APIFORGE_CACHE"]).expanduser()
        if env.get("APIFORGE_CACHE")
        else state_root / "cache"
    )
    return ForgePaths(
        package_root=package_root.resolve(),
        state_root=state_root.resolve(),
        config_path=config_path.resolve() if config_path else None,
        cache_root=cache_root.resolve(),
    )
```

The implementation must validate allowed roots and writability before creating
directories. It must report the resolved paths in `doctor` and never fall back
silently to a read-only package directory.

### Pattern 3: Deterministic root discovery

Discovery is a bounded read-only walk. Each candidate is retained as an evidence
record so a nested invocation can explain why a root was selected.

```python
from collections.abc import Iterator
from pathlib import Path


def ancestors(start: Path) -> Iterator[Path]:
    current = start.resolve()
    while True:
        yield current
        if current.parent == current:
            return
        current = current.parent


def find_repo_root(start: Path) -> Path | None:
    for candidate in ancestors(start):
        if (candidate / ".git").exists():
            return candidate
    return None


def find_project_manifest(start: Path) -> Path | None:
    for candidate in ancestors(start):
        manifest = candidate / ".apiforge" / "project.yaml"
        if manifest.is_file():
            return manifest
    return None
```

Workspace discovery runs only after repository/project resolution and searches
parent directories for `.apiforge/workspace.yaml`, unless an explicit override
is supplied. It never scans an unbounded filesystem tree by default.

### Pattern 4: Evidence-labelled workspace graph

Use the existing graph contracts and evidence levels. A relationship is a claim
with source references, not a bare boolean.

```python
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceRecord


class WorkspaceRelation(VersionedContract):
    relation: Literal["contains", "depends_on", "client_of", "calls", "deploys"]
    source: str
    from_id: str
    to_id: str
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    limitations: tuple[str, ...] = ()


def classify_relation(relation: WorkspaceRelation) -> str:
    return relation.evidence.level
```

Observed manifest or scanner output may be used for `observed`; explicit user
configuration is `declared`; bounded parser inference is `inferred` or
`heuristic`; missing proof remains `unresolved`. The graph builder must not
upgrade a relation merely because its names look plausible.

### Pattern 5: Canonical surface projection

The application facade returns a typed result once. CLI, MCP, Rich and TUI call
the same projector, following the existing `ExperienceSnapshot` pattern.

```python
def context_command(root: Path, scope: str, target: str | None) -> None:
    from apiforge.application.context import resolve_context
    from apiforge.cli import _echo_json, _run

    snapshot = _run(lambda: resolve_context(root, scope=scope, target=target))
    _echo_json(snapshot, detail_level="normal")
```

MCP tools call the same application function and record economy bytes through the
existing `_call` helper. Presentation code may change labels or formatting, but
never infer success, discard unresolved diagnostics or alter evidence levels.

### Pattern 6: Approval-gated host output

Host generation reuses `ActionPlan`/`ActivationPlan`. The renderer returns a
preview and provenance; a separate policy path decides whether any write is
allowed.

```python
def render_host_preview(host: str, root: Path) -> dict[str, object]:
    plan = build_activation_plan(host, str(root))
    return {
        "host": plan.host,
        "mode": plan.execution_mode,
        "requires_approval": plan.approval_required,
        "artifacts": plan.repository_artifacts,
        "limitations": plan.limitations,
        "evidence": plan.evidence,
        "mutation": "none",
    }
```

The default command is preview/plan-only. Conflict, missing permission and
source-hash mismatch are structured refusals with `field` and `unlock`, and new
codes are catalogued before implementation is shipped.

---

## Data Flow

```text
1. User invokes the installed executable from any directory.
   │
   ▼
2. Distribution paths resolve package resources, explicit environment paths,
   project state and optional cache; doctor records the resolution.
   │
   ▼
3. Root discovery finds module, repository, project manifest and parent workspace
   using bounded read-only ancestor checks.
   │
   ▼
4. Configuration resolver merges defaults → global config → workspace manifest
   → project manifest → explicit CLI flags; task/feature precedence is deferred.
   │
   ▼
5. Read-only scanners and declared manifest relations produce facts, graph nodes,
   graph edges, hashes, evidence levels and unresolved diagnostics.
   │
   ▼
6. Context service validates repo/workspace/target scope, applies impact filters
   and invokes the existing byte-measured funnel.
   │
   ▼
7. Application facade emits one typed portable/workspace/context result with
   actions, gaps, evidence refs and safe unlocks.
   │
   ▼
8. CLI, Rich/TUI, MCP stdio and host activation project the same result.
```

No step executes consumer application code, mutates a provider, starts a network
daemon or promotes an external claim without its own receipt.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| Installed Python package | `importlib.resources` package-data read | None |
| Consumer filesystem | Read-only discovery; explicit creation of minimal manifests | Local OS permissions; no secret values |
| Git repositories | Read-only `.git` marker and repository path inspection | None |
| Local cache | Content-addressed local files and existing economy/evidence stores | Filesystem permissions |
| MCP client | Optional local stdio process | Host-owned process registration; no listening port required |
| Claude/Devin/Codex/Copilot | Optional plan/diff/generated adapter | Host-specific capability and explicit approval |
| External freshness/provider systems | Existing read-only adapters only | Host-owned credentials and independent receipts |
| Cloud, database and broker systems | Not required for first wave | No first-wave live access |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Frozen contracts, path normalization, config precedence, scope validation and evidence classification | `tests/contracts`, `tests/distribution`, `tests/context` | pytest, Pydantic validation | Every contract field, invalid enum/path and refusal path |
| Unit | Root discovery, asset loading, source-hash verification and graph ID stability | `tests/workspace`, `tests/distribution`, `tests/host_assets` | pytest, `tmp_path` | Nested paths, missing roots, stale assets, malformed manifests |
| Integration | Project init, workspace add/discover/status and context funnel against temp independent repos | `tests/workspace`, `tests/context`, `tests/e2e` | pytest fixtures | Repo, workspace and target scopes with no monorepo assumptions |
| Integration | Host activation preview, conflict detection and no-overwrite behavior | `tests/agentops`, `tests/host_assets` | pytest, fake filesystem | Every declared host and generated adapter path |
| Integration | CLI/MCP/JSON/Rich/TUI canonical payload parity | `tests/mcp`, `tests/application`, `tests/e2e` | pytest snapshots/goldens | Same status, gaps, evidence, limitations and codes across surfaces |
| E2E | User-selected prefix, offline mode, missing host and blocked network | `tests/e2e/test_portable_distribution.py` | pytest, temporary subprocess environment | Local operation continues while optional gaps remain explicit |
| E2E | Multi-repository graph and targeted context funnel | `tests/e2e/test_workspace_context.py` | pytest, synthetic workspace fixtures | Stable IDs, impact narrowing and unresolved edges |
| Holdout | Ambiguous names, malformed manifests, unsupported framework and missing package data | `tests/fixtures/**` | pytest holdout cases | No heuristic promotion or silent fallback |
| Mutation | Remove evidence, alter source hash, inject conflicting host file or bypass approval | `tests/host_assets`, `tests/context`, `tests/e2e` | existing mutation/eval conventions | Gate must detect missing proof and unsafe overwrite |
| Static/release | Lint, typing, package contents, SDD and documentation links | repository CI and release checks | Ruff, mypy, package build, SDD check | No import of provider SDKs in core; docs and contracts ship together |

Testing follows the KB fixture and integration patterns: use isolated temporary
directories, factories for repeated repository layouts, explicit boundary cases
and deterministic golden payloads. No live cloud, database, provider or host
mutation is required for this feature.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| User-selected path does not exist or is not writable | Return structured `AF-DIST-PATH-INVALID` with `field=path` and unlock to choose/create a writable prefix; do not write | No |
| Package asset missing or hash mismatch | Return `AF-DIST-ASSET-MISSING` or `AF-DIST-ASSET-DIVERGED`, identify the asset and reinstall/repair unlock | No automatic retry |
| No project/repository root found | Return `AF-ROOT-NOT-FOUND` with explicit `--project-root`/`--workspace-root` unlock | No |
| Project/workspace manifest malformed | Return `AF-MANIFEST-INVALID` with path and schema field; preserve the invalid file | No; user edits or regenerates explicitly |
| Workspace repository path missing | Keep repository entry unresolved and return `AF-WORKSPACE-REPO-MISSING` with a path correction unlock | No |
| Unsupported or ambiguous graph relation | Emit an unresolved diagnostic with evidence and limitation; never promote to confirmed | No |
| Network/host/provider unavailable | Continue local operation; mark optional capability `unavailable` or `unresolved` in doctor and context | No |
| Host output conflicts with user-owned file | Return preview/diff and `AF-HOST-CONFLICT`; require explicit approval path | No automatic overwrite |
| Invalid scope or target | Return `AF-CONTEXT-SCOPE-INVALID` with valid scope vocabulary and target discovery unlock | No |
| MCP optional dependency absent | Return `AF-MCP-OPTIONAL-UNAVAILABLE` while CLI remains usable | No |

All new refusal codes must be added to `docs/catalog-contract.md` before build
completion. The public payload includes `code`, rejected `field`, `detail`,
`unlock` and any evidence/limitations available at the point of refusal.

---

## Configuration

First-wave precedence is explicit CLI flag → project manifest → workspace
manifest → user config path → Forge defaults. Feature/task layers are deferred
as required by the DEFINE.

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `APIFORGE_HOME` | path | unset; project state remains under resolved `.apiforge` | User-selected runtime/cache root for restricted or portable environments |
| `APIFORGE_CONFIG` | path | unset | Optional user config file; absence is not an error |
| `APIFORGE_CACHE` | path | unset; `<state_root>/cache` | Explicit cache override |
| `APIFORGE_PROJECT_ROOT` | path | unset; discovered from cwd | Explicit project root override |
| `APIFORGE_WORKSPACE_ROOT` | path | unset; discovered from parent | Explicit workspace root override |
| `scope.default` | `repo\|workspace\|target` | `repo` | Default context scope when no CLI flag is supplied |
| `evidence.strict` | boolean | `true` | Preserve gaps and refuse unsupported confirmation |
| `host.activation.mode` | `plan_only\|approval_required` | `plan_only` | Prevent implicit host mutation |
| `network.mode` | `offline_first\|optional` | `offline_first` | Network is never required for local analysis |
| `workspace.discover_parent` | boolean | `true` | Search parent directories for workspace manifest |
| `assets.verify_hashes` | boolean | `true` | Verify packaged/generated asset correspondence |

Values are loaded into frozen contracts. Secret material is never accepted from
project/workspace manifests or serialized context. Host credentials continue to
belong to the host-owned adapter boundary.

---

## Security Considerations

- Treat current directory, manifest contents, repository names and graph edges as
  untrusted input; validate with Pydantic and closed vocabularies.
- Resolve and normalize paths before access; reject traversal outside explicit
  project/workspace/prefix boundaries and report the rejected field.
- Never execute consumer code, shell hooks, agent prompts or host configuration
  during discovery. Scanners remain static/read-only.
- Keep secrets, tokens, credentials and provider payloads out of manifests,
  graph properties, prompts, logs, receipts and generated adapters.
- Use `importlib.resources` and source hashes for package assets; do not load
  authority from a cwd-controlled mirror when the installed package is present.
- Host generation is a preview/diff action. Overwrite requires a separate policy,
  approval, rollback path and receipt; symlink remains deferred.
- Network and external integrations are disabled or optional by default. A
  missing external receipt remains unresolved rather than becoming a claim.
- Preserve the existing core boundary: no OpenAI/Anthropic/LiteLLM SDK imports
  in `src/`, no live AWS/database mutation and no implicit PR/provider mutation.
- Add refusal codes and safe unlocks to the catalog before exposing new public
  commands or MCP tools.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured local diagnostics containing command, resolved roots, scope, path source, asset state and refusal code; never secrets |
| Metrics | Reuse economy ledger for payload bytes/detail level and add local discovery/cache hit counters without claiming production performance |
| Tracing | Reuse existing provenance/evidence graph, artifact hashes and receipts; each graph/context output references source paths and limitations |
| Doctor | Canonical capability matrix for package, path, cache, host, MCP, network and optional extras with explicit `ready`, `unavailable`, `degraded` or `unresolved` states |
| Reproducibility | Stable manifest/graph IDs, sorted collections, deterministic JSON/YAML and source hashes |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-24 | design-agent | Initial architecture and technical specification from validated DEFINE |
| 1.1 | 2026-09-24 | build-agent | Portable distribution, workspace/context services, host asset provenance, CLI/MCP surfaces, contracts, tests and documentation built and verified |
| 1.2 | 2026-09-24 | ship-agent | Shipped and archived with verified build evidence |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_PORTABLE_DISTRIBUTION_WORKSPACE/`
