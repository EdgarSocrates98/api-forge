# DEFINE: API Forge Agent Roster — Consolidate + Enrich, Host-Neutral

> Replace 52 mostly-stub coordinators with 25 contract-complete, English, least-privilege agents rendered from one source to Claude Code, Devin and Codex, guarded by render-drift, contract-lint, referential-integrity, audit and routing-eval gates.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENT_ROSTER |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_API_FORGE_AGENT_ROSTER.md` |
| **Branch** | `sdd/agent-roster` (stacked on `sdd/new-forge` @ 9cbe0fe) |

---

## Problem Statement

The 52 coordinators in `agents/*.md` do not behave as distinct specialists: 28 bodies are under 35 words, `apiforge agents audit` flags 44 as merge-candidates, descriptions mix PT and EN and often cannot route, no agent declares permissions, and the Codex mirror (`.codex/agents`) lives outside sync and the release gate (while `agentops/parity.py` points Codex at `.agents/agents`). Agent quality therefore depends on the host, not on the project.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Owner/maintainer | Curates roster, reviews routing | Cannot tell agents apart; 44 flagged redundant; three mirrors to keep in sync |
| Host router (Claude Code, Devin, Codex) | Picks an agent from descriptions | Weak/mixed-language descriptions → misrouting |
| Dispatched agent | Executes a role | No explicit inputs, method, output, done criterion or refusal path |
| Verifier / critic / referee | Judge agent output | Nothing to check the output against; independence not declared |
| Replay/eval consumer | Re-runs stored decisions | Renames would break stored `routing.json`/`replay.json` |

---

## Goals

### Wave 1 — Infrastructure and gates

| Priority | Goal |
|----------|------|
| **MUST** | W1-1: Host-neutral source frontmatter schema: `name`, `description`, `access` (`read-only`\|`writer`), `write_scope` (writers only), `model_tier` (`fast`\|`deep`), `rule_areas`, `executors`, `apiforge_tools` (renamed from `tools`), `replaces` (absorbed old names) |
| **MUST** | W1-2: Deterministic renderer `agents/*.md` → `.claude/agents/*.md` (name, description, `tools` from access, optional `model` from tier), `.agents/agents/*.md` (name, description only), `.codex/agents/*.toml` (name, description, developer_instructions, `sandbox_mode` from access, optional `model_reasoning_effort` from tier) |
| **MUST** | W1-3: Render-drift gate: each mirror equals `render(source, host)`; `.codex` included; orphans (`.md`, `.toml`) fail; TOML parses; `name` = filename = source name |
| **MUST** | W1-4: Contract lint: 9 body sections (When you enter, When not to enter, Inputs, Method, Output, Done when, Refusal and escalation, Permissions, Executors), body 250–600 words, English, description ≤300 chars containing "Use when" and "Not for" |
| **MUST** | W1-5: Referential integrity gate: every agent name in `src/apiforge/rules/*.yaml`, `src/apiforge/**/*.py`, `tests/**`, `evals/**` ∈ roster ∪ aliases |
| **MUST** | W1-6: `src/apiforge/rules/agent_aliases.yaml` (old → new, `deprecated_in`); dispatch, routing, runtime and replay resolve aliases and emit `AF-AGENT-ALIAS-DEPRECATED` (warning, cataloged) |
| **MUST** | W1-7: Routing eval `evals/corpus/agent-routing/` (60–100 golden question → agent cases) + `apiforge evals agent-routing` with accuracy and per-family misroute report |
| **MUST** | W1-8: Fix `agentops/parity.py` mapping gpt-codex → `.codex/agents` |
| **SHOULD** | W1-9: `apiforge agents render [--check]` CLI (write vs verify) and MCP parity if a mirror/audit tool exists there |

### Wave 2 — Content and migration

| Priority | Goal |
|----------|------|
| **MUST** | W2-1: 25 agents (roster below), English, 9 sections, least privilege, each owning ≥1 unique capability in the runtime capability catalog or a unique decision role |
| **MUST** | W2-2: Remove the 27 absorbed agent files from `agents/`; mirrors regenerated; old names only in `agent_aliases.yaml` and `replaces` |
| **MUST** | W2-3: Migrate names in rules (`playbooks.yaml`, `catalog/routing.yaml`, `agent_profiles.yaml`, `agentic_runtime.yaml`, `routing.yaml`, `capability_matrix.yaml`), code (`runtime/supervisor.py` ×6, `runtime/review.py`), tests (11 files), evals (`economy-replay/*.json`, `skills/evals.json`) |
| **MUST** | W2-4: Re-record `evals agentic-quality` baseline with a written justification (names changed, behavior preserved) stored as SDD evidence |
| **SHOULD** | W2-5: Update routing docs (`AGENTS.md`, `CLAUDE.md` routing, `README.md`, `docs/integrations/API_FORGE_DEVIN*`, `.devin/agents/api-forge-reviewer.md`) to new names |
| **COULD** | W2-6: `AGENT_PROTOCOL.md` gains a short "agent contract" section referenced by all bodies |

### Roster (25)

| # | Agent | Absorbs | Access |
|---|-------|---------|--------|
| 1 | api-orchestrator | api-agentic-orchestrator, api-agentic-observability-engineer, api-grpc-agentic-engineer | writer (ledger) |
| 2 | api-planner | api-runtime-migration-planner | writer (plans) |
| 3 | api-task-spec-reviewer | — | read-only |
| 4 | api-platform-selector | — | read-only |
| 5 | api-architecture-reviewer | — | read-only |
| 6 | api-infra-reviewer | terraform-reviewer, aws-api-infra-reviewer, api-drift-reconciliation-engineer | read-only |
| 7 | api-contract-architect | api-grpc-contract-engineer, api-grpc-parser-engineer, api-grpc-gateway-engineer | read-only |
| 8 | api-governance-reviewer | api-grpc-compatibility-engineer | read-only |
| 9 | api-codegen-engineer | api-grpc-codegen-engineer, api-grpc-toolchain-engineer | writer (worktree) |
| 10 | api-security-reviewer | api-grpc-security-engineer, api-observability-security-engineer | read-only |
| 11 | api-data-access-architect | api-relational-data-architect, api-analytical-data-architect | read-only |
| 12 | api-event-driven-architect | api-streaming-platform-architect | read-only |
| 13 | api-resilience-engineer | api-grpc-runtime-engineer, api-slo-reliability-engineer | read-only |
| 14 | api-performance-engineer | api-grpc-performance-engineer | read-only |
| 15 | api-load-capacity-engineer | api-load-test-engineer, api-capacity-engineer | writer (scenarios) |
| 16 | api-observability-engineer | api-instrumentation-engineer, api-grpc-observability-engineer, api-telemetry-normalization-engineer | read-only |
| 17 | api-observability-integration-engineer | api-observability-control-plane, api-vendor-integration-engineer, api-datadog-integration-engineer, api-dynatrace-integration-engineer | writer (projections) |
| 18 | api-test-strategist | — | read-only |
| 19 | api-dx-docs-reviewer | — | read-only |
| 20 | api-modernization-specialist | — | read-only |
| 21 | api-operations-engineer | — | read-only |
| 22 | api-verifier | api-verification-engineer, api-runtime-migration-verifier, api-platform-completion-reviewer | read-only |
| 23 | api-adversarial-critic | — | read-only |
| 24 | api-debate-referee | — | read-only |
| 25 | api-release-guardian | — | writer (release artifacts) |

Every one of the 52 current names maps to exactly one roster entry (kept or absorbed).

---

## Success Criteria

- [ ] `apiforge agents audit` over `agents/` → exactly 25 agents, 25 `keep`, 0 `merge-candidate`.
- [ ] Contract lint: 25/25 agents pass (9 sections, 250–600 body words, EN, description ≤300 chars with "Use when" and "Not for").
- [ ] Render-drift gate: 0 drift across 75 generated files (25 × 3 hosts); 0 orphans; release gate green.
- [ ] Access projection: 100% of read-only agents render without write tools (Claude) and `sandbox_mode = "read-only"` (Codex); writers render `workspace-write` and declare `write_scope`.
- [ ] Referential integrity: 0 names outside roster ∪ aliases in rules/code/tests/evals.
- [ ] Alias table covers 27/27 absorbed names; every alias resolves to a roster agent; replay of `evals/corpus/economy-replay` passes with old names.
- [ ] Routing eval: ≥60 golden cases; accuracy on post-change roster ≥ accuracy measured on the pre-change roster with alias mapping; 0 cross-family misroutes among critic/referee/verifier.
- [ ] `parity.py` gpt-codex target = `.codex/agents`.
- [ ] Full suite green (excluding the pre-existing untracked `.claude/agents/README.md` orphan, which the render gate must now report distinctly), `apiforge sdd check`, `evals economy-hardening`, `evals agentic-quality --baseline <re-recorded>` green.
- [ ] Renderer idempotent: two consecutive renders produce byte-identical output.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Render all hosts | Valid source agent (read-only, tier deep) | `agents render` | Claude md has name/description/tools without Edit/Write; Devin md has only name/description; Codex toml has developer_instructions = body and `sandbox_mode = "read-only"` |
| AT-002 | Writer projection | Source `access: writer`, `write_scope: plans/` | render | Claude tools include Edit/Write; Codex `sandbox_mode = "workspace-write"`; body Permissions section names the scope |
| AT-003 | Drift detected | `.codex/agents/x.toml` edited by hand | `agents render --check` / release gate | Fails with drift path; `--check` never writes |
| AT-004 | Orphan detected | Extra `.codex/agents/old.toml` or `.claude/agents/old.md` | gate | Reported as orphan |
| AT-005 | Idempotence | Rendered tree | render twice | No file changes |
| AT-006 | Contract lint failure | Body missing "Done when" or 180 words, or PT description | lint | Refused `AF-AGENT-CONTRACT-*` with field + unlock |
| AT-007 | Writer without scope | `access: writer`, no `write_scope` | lint | Refused |
| AT-008 | Alias resolution | Playbook or replay references `api-grpc-parser-engineer` | dispatch/replay | Resolves to `api-contract-architect`; warning `AF-AGENT-ALIAS-DEPRECATED` |
| AT-009 | Unknown name | Rule references `api-nonexistent` | referential gate | Fails naming file:line |
| AT-010 | Alias to missing target | Alias points to non-roster agent | gate | Fails |
| AT-011 | Audit | Final roster | `agents audit` | 25 keep, 0 merge-candidate |
| AT-012 | Routing eval | Golden corpus | `evals agent-routing` | Accuracy ≥ baseline; report per family |
| AT-013 | Critic independence | Golden cases for critic/referee/verifier | routing eval | Each routes to its own agent; never merged |
| AT-014 | Codex parity map | `agentops parity` for gpt-codex | inspect | Target `.codex/agents` |
| AT-015 | Supervisor | Runtime run that previously used `api-agentic-orchestrator` | execute | Uses `api-orchestrator`; stored old-name runs still load |

---

## Out of Scope

- Per-agent answer-quality golden evals.
- Rewriting `agents/executors/af-*`.
- Family skills (gRPC, vendors) as a replacement for agents.
- Concrete per-host model IDs (only `model_tier`).
- Translating user-facing docs to English.
- Removing aliases (next release).
- Rich Devin frontmatter beyond name/description.
- New agents beyond the 25.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | `agents/*.md` is the only hand-edited agent source; mirrors are generated | Renderer + gate own `.claude/agents`, `.agents/agents`, `.codex/agents` |
| Technical | Source key `tools` is read by `agentops/agent_audit.py` as API Forge tools; Claude `tools` means host tools | Rename source key to `apiforge_tools`; audit reads it; Claude `tools` only in rendered output |
| Technical | `.claude/agents/` also holds non-generated content (`custom/`, `workflow/`, untracked `README.md`) | Gate scopes to generated `*.md` at top level; non-generated paths reported distinctly, never deleted |
| Technical | Offline, no provider SDK, no host API | Pure render |
| Technical | AF refusals with code, field, unlock; cataloged | New `AF-AGENT-CONTRACT-*`, `AF-AGENT-ALIAS-*`, `AF-AGENT-RENDER-*` |
| Governance | Critic, referee, verifier remain distinct agents | Roster rows 22–24 fixed |
| Process | Wave 1 merged gates must pass before Wave 2 content lands | Build order |
| Process | Eval baseline re-record only with written justification | SDD evidence |
| Process | Targeted tests per task; full suite once before ship; basetemp `E:/afpt` | Build strategy |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `agents/`, `src/apiforge/dispatch/` (render, mirrors, aliases), `src/apiforge/agentops/{agent_audit,parity}.py`, `src/apiforge/rules/*.yaml`, `src/apiforge/runtime/{supervisor,review}.py`, `scripts/check_release.py`, `evals/corpus/agent-routing/`, `docs/sdd/API_FORGE_AGENT_ROSTER/` | Extends existing mirror/audit modules |
| **KB Domains** | agentspec: `anti-patterns`, `component-model`; project skills: `api-forge-context`, `api-forge-sdd`, `api-forge-verification` | Agent contracts, gates, independent verification |
| **IaC Impact** | None | Local-only |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Claude Code tolerates extra frontmatter keys only if we strip them; renderer emits only documented keys | If extra keys break loading, already mitigated by minimal render | [ ] |
| A-002 | Devin reads `.agents/agents/*.md` with name/description frontmatter | Devin routing degrades; keep md body identical | [ ] |
| A-003 | Codex honors `sandbox_mode` and `model_reasoning_effort` in custom agent TOML (per docs fetched 2026-09-28) | Drop optional keys | [x] (doc) |
| A-004 | Each of the 25 can own ≥1 unique runtime capability or decision role without inventing fake capabilities | Audit < 25 keep; merge further or accept documented exception | [ ] |
| A-005 | 60–100 golden routing cases can be derived from existing tests/routing tables without owner authoring | Owner writes additional cases | [ ] |
| A-006 | Stored replays reference agents only through fields the alias resolver sees | Some replays fail; add resolver hook | [ ] |
| A-007 | Behavior preserved enough that agentic-quality differences are name-only | Baseline re-record hides regression; critic reviews diff | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Quantified with repo evidence |
| Users | 3 | Five roles incl. hosts and replay consumers |
| Goals | 3 | MoSCoW per wave; roster fixed |
| Success | 3 | Numeric gates, reproducible commands |
| Scope | 2 | Clear; A-004 may force a roster exception |
| **Total** | **14/15** | |

---

## Open Questions

- Exact `model_tier` defaults per agent (design decision).
- Whether `apiforge agents render` also needs an MCP tool (depends on existing MCP agent tools; design checks).

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial version from BRAINSTORM |
| 1.1 | 2026-09-28 | ship-agent | Shipped and archived |

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_AGENT_ROSTER.md`
