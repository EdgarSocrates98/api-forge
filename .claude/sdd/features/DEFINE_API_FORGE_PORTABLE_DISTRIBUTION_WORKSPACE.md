# DEFINE: API Forge Portable Distribution, Workspace and Host Activation

> Transform API Forge from a repository-copied toolkit into an installed, portable and host-agnostic engineering platform.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_PORTABLE_DISTRIBUTION_WORKSPACE |
| **Date** | 2026-09-24 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 15/15 |

---

## Problem Statement

API Forge currently exposes a deterministic Python package, CLI, MCP and host assets, but its documented operating model still encourages work inside the API Forge repository and mirrors large `.claude`, `.agents`, `.devin` and `.github` trees into projects. Developers, platform teams, host maintainers and users in restricted environments need an installed, portable and host-agnostic Forge that resolves repository or workspace context without requiring copied knowledge, a monorepo, network access or administrator privileges.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| API developer | Uses API Forge from a project or nested source directory | Needs discovery, context, SDD, agents, skills, graph, evidence and verification without copying API Forge assets into the project |
| Platform engineer | Operates several independent services, SDKs and infrastructure repositories | Needs a virtual workspace, bounded architecture graph, impact scopes, cache and configuration without creating a monorepo |
| Host integration maintainer | Connects Claude, Devin, Codex, Copilot or MCP to API Forge | Needs small, explicit and evidence-aware adapters without making host capabilities look equivalent or mandatory |
| Restricted-environment user | Works without admin rights, network access or unrestricted host configuration | Needs user-selected installation paths and the maximum local API Forge capability even when optional integrations are unavailable |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Distribute API Forge as an installable package whose core owns agents, skills, knowledge, contracts, SDD, graph, evidence, verification and host-neutral execution. |
| **MUST** | Support user-local, virtual-environment and user-selected-prefix installation without administrator privileges, with executable discovery through explicit environment configuration or absolute paths. |
| **MUST** | Provide hostless local operation for `inspect`, `init`, `status`, `doctor` and `context`, including offline and network-restricted execution with optional capability gaps preserved as `unresolved`. |
| **MUST** | Resolve current module, repository and parent workspace, and persist minimal project/workspace manifests without requiring a monorepo or copying the Forge knowledge base. |
| **MUST** | Produce evidence-backed repository, service, contract, dependency, runtime and architecture representations with repo, workspace and target scopes. |
| **MUST** | Keep host activation, MCP and generated mirrors optional, explicit, capability-aware and approval-gated where they mutate a repository or host configuration. |
| **MUST** | Update all affected documentation, contracts, examples, host guidance, migration notes, security limits and roadmap entries before ship, and preserve a traceable commit. |
| **SHOULD** | Reuse one canonical service and projection model across expert CLI, human CLI, MCP, TUI/Rich/JSON and host adapters. |
| **SHOULD** | Support local cache and packaged knowledge so analysis remains useful when network, provider, credentials, host or optional dependency is missing. |
| **SHOULD** | Make generated host artifacts deterministic, provenance-labelled and source-hash-aware without overwriting user changes automatically. |
| **COULD** | Add richer onboarding, workspace discovery suggestions, migration helpers and human-mode orchestration after the portable core is stable. |

**Priority Guide:**
- **MUST** = MVP fails without this
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes (must include numbers):

- [ ] The first release supports at least **four** installation paths in the acceptance matrix: user-local tool, virtual environment, explicit user-selected prefix and portable/container path.
- [ ] The human entry surface exposes the **five** core actions `inspect`, `init`, `status`, `doctor` and `context` without requiring a host, network port or provider SDK.
- [ ] Context resolution validates all **three** scopes: repo, workspace and target; nested-directory discovery must resolve the same project/workspace identity as invocation from its root.
- [ ] The offline test matrix covers at least **three** optional-unavailability cases: blocked network, missing host and missing external/provider capability, with local work continuing and the gap named.
- [ ] Workspace fixtures preserve independent `.git` directories and verify that project/workspace manifests do not merge or rewrite repository history.
- [ ] Architecture graph fixtures distinguish observed, declared and inferred relationships and retain evidence references, hashes and `unresolved` diagnostics for unsupported inference.
- [ ] Host activation tests cover every currently declared host adapter and prove that plan-only inspection does not mutate consumer files or host configuration.
- [ ] Documentation acceptance covers README, project/workspace guides, installation and restricted-environment guidance, contracts, host/MCP docs, migration notes, troubleshooting and roadmap.
- [ ] Validation includes focused unit/integration tests, projection or golden fixtures, holdout cases where applicable, mutation checks where applicable, `ruff`, mypy, relevant SDD gates and a traceable commit.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | User-selected installation | A user has a writable prefix but no administrator privileges | API Forge is installed into that prefix and the executable directory is placed on `PATH` or invoked absolutely | `doctor` resolves the installed package and bundled assets without requiring a system-wide installation |
| AT-002 | Hostless offline operation | The network is blocked and no agent host is configured | The user runs `inspect`, `status`, `doctor` and `context` against a local project | Local analysis, rules, agents, skills, SDD, graph, evidence and verification remain available; unavailable optional capabilities are named as `unresolved` |
| AT-003 | Nested root discovery | The current directory is below a repository with an optional parent workspace | The user invokes `context` from a nested module | The result identifies module, repository and workspace scope using deterministic precedence and path evidence |
| AT-004 | Minimal project initialization | A consumer repository has no API Forge files | The user runs `apiforge init` | Only the minimal project manifest and explicitly requested adapters are created; the full knowledge, agents and skills are not copied |
| AT-005 | Independent workspace | Several sibling repositories each retain their own `.git` directory | The user runs workspace discovery or adds repositories explicitly | A workspace manifest and evidence-backed graph are created without converting the repositories into a monorepo or mutating their Git metadata |
| AT-006 | Targeted context funnel | A workspace contains unrelated repositories and a request names a target service | The user requests `context` with repo, workspace or target scope | The output narrows context by selected scope and impact, preserves source references and reports excluded or unresolved edges |
| AT-007 | Graph evidence boundary | A relationship is observed in a manifest, declared by a user or only heuristically suggested | Discovery builds architecture IR | The relationship type and provenance are distinct; heuristics cannot be emitted as confirmed facts |
| AT-008 | Restricted optional capability | A host, network, credential, optional dependency or provider is unavailable | The user runs `doctor` and a local analysis | The result distinguishes unavailable optional capability from invalid installation and provides a safe unlock without blocking local work |
| AT-009 | Host activation safety | A host adapter can be generated but the consumer project contains user-owned files | The user requests a host activation plan or sync preview | The default result is plan-only/diff-oriented, includes source hash and limitations, and does not overwrite files automatically |
| AT-010 | Local MCP | The environment permits local process execution but not a network daemon | The user starts the MCP entrypoint over stdio | MCP exposes the same canonical read/compose capabilities as CLI projections without requiring a listening port |
| AT-011 | Compatibility | Existing expert CLI, MCP and JSON consumers are present | The new human/project/workspace surfaces are exercised | Existing expert commands and canonical payload semantics remain compatible or report an explicit versioned migration |
| AT-012 | Documentation and release gate | The feature changes installation, context, workspace, host and security behavior | The release validation runs | All affected documentation and roadmap sections are present, tests and SDD checks pass, unresolved gaps are reported and the change has a traceable commit |

---

## Out of Scope

Explicitly NOT included in this feature's first wave:

- Autonomous high-level orchestration through `ask`, `improve`, `migrate` and `fix`.
- Complete relationship inference across every repository, language, provider and infrastructure type.
- A separate `apiforge here` command before internal context resolution is stable.
- Auto-update and remote Knowledge Pack updates.
- Symlink as a default or guaranteed installation mode.
- Automatic host synchronization that overwrites user-owned files.
- Full configuration precedence down to task scope before default/global/workspace/project manifests stabilize.
- Distributed multi-agent debate across a workspace.
- Any promise of total functional parity between Claude, Devin, Codex, Copilot or other hosts without per-capability evidence.
- A mandatory monorepo, mandatory network service, mandatory remote MCP, web UI as the primary surface, provider mutation or production claims without independent receipts.

The deferred items remain in the roadmap and must return to SDD discovery after this feature ships and is committed.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Core remains offline-first and must not import model/provider SDKs | External freshness, model access and host capabilities are adapters or optional integrations, never core prerequisites |
| Technical | Installation must support a user-selected writable path and no administrator privileges | Package resolution, bundled assets, executable paths and `doctor` must work from explicit prefixes, virtual environments and portable locations |
| Technical | Project and workspace state must remain minimal and versioned | Manifests hold connection and override metadata; knowledge, agents and skills remain in the installed Forge |
| Technical | Independent repositories keep their own Git metadata | Workspace graph operates virtually above repository roots and does not force monorepo restructuring |
| Technical | Observed, declared, inferred and unresolved states must remain distinct | Graph and context outputs cannot promote heuristic or fixture information to confirmed runtime claims |
| Technical | Host changes require explicit action and policy | Activation plans, diffs, provenance and approval are required before mutating host or consumer files |
| Compatibility | Existing expert CLI, MCP, JSON, mirrors and contracts must remain usable during migration | New human and workspace surfaces are additive and versioned; breaking changes require explicit migration evidence |
| Security | Blocked network, missing credentials and restricted filesystem access are expected states | `doctor` diagnoses them separately and local capabilities continue where safe |
| Documentation | All affected documentation must be updated before ship | README, guides, contracts, host/MCP docs, migration, troubleshooting, security and roadmap are release artifacts |
| IaC | No cloud or infrastructure mutation is required for the first wave | Local filesystem, package installation, cache and optional container/volume paths are the deployment surfaces |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge` plus package metadata; tests under `tests/fixtures/portable_distribution` and `tests/fixtures/workspaces`; docs and versioned contracts under `docs/` | Add distribution, root resolution, manifest, workspace, graph and host activation services without making host mirrors the source of truth |
| **KB Domains** | `genai`, `python`, `pydantic`, `testing`, `prompt-engineering` | Consult state machines, tool calling, guardrails, clean architecture, typed models, fixtures, integration testing, system prompts and structured output |
| **IaC Impact** | None for the first wave | No cloud resource is required; containers or volumes are optional local installation targets and must not become prerequisites |

**Why This Matters:**

- **Location** → Design phase uses the existing Python package and bounded contexts instead of adding an unrelated launcher tree.
- **KB Domains** → Design phase gets patterns for deterministic orchestration, typed manifests, portable context and fixture-based validation.
- **IaC Impact** → Infrastructure planning is explicitly not required for the first distribution slice.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | The package build can include or resolve bundled agents, skills, knowledge and contracts independently of the current working directory | Distribution would still depend on repository checkout assets and fail the portability goal | [ ] |
| A-002 | Supported Python environments permit user-local or explicit-prefix installation without administrator privileges | A bootstrap or alternate launcher would be required for restricted machines | [ ] |
| A-003 | The executable directory can be added to `PATH` or invoked through an absolute path in supported environments | `doctor` and docs would need a host-specific launcher registration mechanism | [ ] |
| A-004 | The existing CLI, MCP and projection contracts can be extended additively | A compatibility migration would be required before the new surfaces ship | [ ] |
| A-005 | Local repository signals are sufficient to build a useful bounded graph without executing consumer applications | More adapters or explicit user declarations would be needed for the first graph slice | [ ] |
| A-006 | A local cache can hold enough packaged or previously collected context for offline operation | The offline promise would need narrower capability claims and clearer exclusions | [ ] |
| A-007 | Host adapters can be represented as explicit capabilities and plan-only actions | Host-specific integrations would need separate product boundaries rather than a shared activation layer | [ ] |
| A-008 | Existing mirrors can remain compatible during a generated-adapter migration | A coordinated host migration would be required before the portable package could ship | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | The portability, repository contamination, host dependency and restricted-environment pains are explicit in the BRAINSTORM and user confirmations |
| Users | 3 | Developer, platform engineer, host maintainer and restricted-environment user are identified with concrete pain points |
| Goals | 3 | MUST/SHOULD/COULD goals cover installation, hostless operation, workspace, graph, evidence, adapters and documentation |
| Success | 3 | Success is expressed through installation modes, core commands, scopes, unavailability cases, host coverage and release evidence |
| Scope | 3 | First-wave boundaries and the complete deferred roadmap are explicit |
| **Total** | **15/15** | Ready for Design under the Define clarity gate |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

The following are Design-phase questions, not blockers for Define:

- What exact bootstrap/install command should support explicit prefixes consistently across Windows, WSL, POSIX and containers?
- Which environment variables and configuration files are canonical for install location, config, cache, project discovery and workspace discovery?
- What is the versioned schema and closed vocabulary for project manifests, workspace manifests, graph nodes, graph edges and evidence states?
- Which repository signals are allowed to create observed, declared and inferred relationships in the first graph slice?
- Which current host mirrors are generated, which remain user-owned, and how should conflicts be surfaced without overwriting them?
- Which package extras are required for core, TUI, MCP and optional integrations, and how should missing extras appear in `doctor`?
- Which documentation files are mandatory in the ship checklist, and how will cross-surface command parity be tested?

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-24 | define-agent | Initial requirements extracted from validated BRAINSTORM |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_PORTABLE_DISTRIBUTION_WORKSPACE.md`
