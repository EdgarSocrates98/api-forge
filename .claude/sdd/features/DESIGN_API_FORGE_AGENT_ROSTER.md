# DESIGN: API Forge Agent Roster — Consolidate + Enrich, Host-Neutral

> Technical design for a single-source, rendered, gated roster of 25 contract-complete agents across Claude Code, Devin and Codex.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENT_ROSTER |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_AGENT_ROSTER.md](./DEFINE_API_FORGE_AGENT_ROSTER.md) |
| **Status** | Ready for Build |
| **Design confidence** | 0.80 (strong codebase patterns: `dispatch/mirrors.py`, `agentops/agent_audit.py`; host formats from official Codex doc; Devin schema unverified) |

---

## Architecture Overview

```text
                       agents/*.md  (ONLY hand-edited source; EN; 9-section body)
                       frontmatter: name, description, access, write_scope?, model_tier,
                                    rule_areas, executors, apiforge_tools, replaces
                                             │
                       dispatch/agent_source.py  parse + validate (AF-AGENT-CONTRACT-*)
                                             │
                    ┌────────────────────────┼─────────────────────────┐
                    ▼                        ▼                         ▼
          render_claude()           render_devin()            render_codex()
   .claude/agents/<n>.md     .agents/agents/<n>.md      .codex/agents/<n>.toml
   name, description,        name, description,         name, description,
   tools (by access),        body                       developer_instructions,
   model (by tier), body                                sandbox_mode (by access),
                                                        model_reasoning_effort (by tier)
                    └───────────── dispatch/render.py (pure; deterministic) ──────┘
                                             │
        apiforge agents render [--check]  ── sync (write) / check (never writes)
                                             │
  scripts/check_release.py ── mirror_drift() = diff(render(source), disk) + orphans
                           ── contract lint (sections, words, EN, description shape)
                           ── referential integrity (rules/code/tests/evals ⊆ roster ∪ aliases)
                           ── agents audit: all keep
                                             │
  rules/agent_aliases.yaml ── dispatch/aliases.py resolve_agent(old) → new + AF-AGENT-ALIAS-DEPRECATED
        consumers: runtime/registry (capabilities, profiles), application/next_step (routes),
                   playbooks loader, runtime store (replay/load of stored runs), evals replay
                                             │
  evals/corpus/agent-routing/*.json ── evals/agent_routing.py
        deterministic proxy router: lexical score over rendered description + "When you enter"
        top-1 / top-3 accuracy, per-family misroute, baseline vs candidate
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `contracts/agents.py` | `AgentSource` (frontmatter + body), `AgentAccess`, `RenderedFile`, `AgentRoutingCase`, `AgentRoutingReport` | pydantic `VersionedContract` |
| `dispatch/agent_source.py` | Parse `agents/*.md`, validate schema + contract lint | yaml, re |
| `dispatch/render.py` | Pure host renderers + `render_all(root) -> dict[path, bytes]` | stdlib, json (TOML basic strings) |
| `dispatch/mirrors.py` | `sync_mirrors`/`mirror_drift` rewritten on top of `render_all`; adds `.codex/agents`; orphans for `.md` and `.toml` at mirror top level only | existing module |
| `dispatch/aliases.py` | Load `rules/agent_aliases.yaml`; `resolve_agent(name) -> AliasResolution` | yaml |
| `dispatch/references.py` | Referential integrity scan (rules YAML keys `agent`/`recommended_agent`/lists; `api-*`/`terraform-reviewer`/`aws-api-infra-reviewer` tokens in py/tests/evals) | re, yaml |
| `agentops/agent_audit.py` | Read `apiforge_tools` (fallback `tools` for one release) | existing |
| `agentops/parity.py` | gpt-codex → `(AGENTS.md, .agents/skills, .codex/agents)` | existing |
| `evals/agent_routing.py` | Deterministic proxy-router eval + report | stdlib |
| `cli_agents` (existing `agents` group) | `agents render [--check]`, `agents lint`, `agents references` | typer |
| `scripts/check_release.py` | Calls drift, lint, references, audit | existing |
| `rules/agent_aliases.yaml` | 27 old → new mappings, `deprecated_in: "roster-v2"` | yaml |
| 25 × `agents/*.md` | Roster content | markdown |

---

## Key Decisions

### Decision 1: Render, don't copy — gate compares against `render(source, host)`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** Mirrors are byte copies today (`dispatch/mirrors.py`). Claude needs `tools`, Codex needs TOML with `sandbox_mode`, Devin needs a minimal frontmatter; byte identity is impossible once hosts diverge.

**Choice:** One pure renderer per host from the parsed source; `sync_mirrors` writes `render_all`, `mirror_drift` diffs it. Output bytes are LF, UTF-8, trailing newline, stable key order.

**Rationale:** Keeps the "drift is a failure" invariant while allowing per-host projection; a single code path for write and check prevents skew.

**Alternatives Rejected:**
1. Three hand-maintained trees + checker — rejected: the `.codex` drift that started this.
2. Host-specific source files — rejected: triples maintenance, breaks single source.

**Consequences:**
- Editing a mirror by hand always fails the gate.
- Renderer changes re-render all 75 files (reviewable diff).

---

### Decision 2: Host-neutral permission model projected per host

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** Least privilege is required; hosts express it differently.

**Choice:** Source `access: read-only | writer` (+ `write_scope` for writers, e.g. `docs/field/`, `.apiforge/`, worktree). Projection:

| Source | Claude `tools` | Codex `sandbox_mode` | Devin |
|--------|----------------|----------------------|-------|
| read-only | `Read, Grep, Glob, Bash` | `read-only` | body Permissions section only |
| writer | `Read, Grep, Glob, Bash, Edit, Write` | `workspace-write` | body Permissions section only |

`model_tier: fast | deep` → Claude `model: sonnet | opus` (omitted when tier absent), Codex `model_reasoning_effort: medium | high`.

**Rationale:** One declaration, enforced where the host supports it, documented in the body where it does not (Devin).

**Alternatives Rejected:**
1. No restriction — rejected by owner (least privilege).
2. Concrete model IDs per host — rejected: IDs churn; tier is stable.

**Consequences:**
- Bash stays available to read-only agents (they run `apiforge` read commands); `Permissions` section forbids mutation explicitly. Host sandbox is the hard boundary only on Codex.

---

### Decision 3: Uniqueness through real `apiforge_tools`, not new runtime capabilities

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** `agents audit` marks `keep` only with a unique capability, rule area, executor, tool or decision role. Only 8 agents own runtime capabilities (`rules/agentic_runtime.yaml`). Adding 17 capabilities would change runtime routing and eval baselines (A-004 risk).

**Choice:** Rename source key `tools` → `apiforge_tools` (audit reads it; falls back to `tools` for one release). Each agent lists the real `apiforge` commands it owns, with no command owned by two agents (e.g. `perf verdict` → load-capacity, `grpc codegen` → codegen, `report sign` → release-guardian, `observability instrument` → observability-engineer, `model terraform` → infra-reviewer). The runtime capability catalog only gets renames.

**Rationale:** Uniqueness reflects real ownership; runtime routing semantics unchanged.

**Alternatives Rejected:**
1. Add 17 `state: supported` capabilities — rejected: silently widens runtime routing.
2. Invent decision roles — rejected: fake uniqueness ("agentic theater").

**Consequences:**
- Adding a command later requires assigning an owner (lint checks duplicates).

---

### Decision 4: Aliases resolved at the edges that read names

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** Old names live in stored runs, replays, user habits; rules will be migrated.

**Choice:** `rules/agent_aliases.yaml`:

```yaml
version: 1
deprecated_in: roster-v2
aliases:
  api-grpc-parser-engineer: api-contract-architect
```

`resolve_agent` is applied where a name enters from data: capability/profile loaders, `next_step` routes, playbook loader, runtime run/replay loaders, evals replay. It returns the canonical name and, when aliased, an `AF-AGENT-ALIAS-DEPRECATED` entry added to the payload's `unresolved`/`warnings` (never an exception). Unknown names keep today's behavior (existing refusals).

**Rationale:** Replays keep working; rules are migrated, so aliases only matter for stored data and humans.

**Alternatives Rejected:**
1. Stub agent files per old name — rejected: pollutes roster and audit.
2. Hard break — rejected by owner.

**Consequences:**
- Referential gate allows alias keys only inside `agent_aliases.yaml`, `replaces:` and stored-evidence fixtures.

---

### Decision 5: Routing eval uses a deterministic proxy router

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** Hosts route with an LLM over descriptions; the repo has no NL router and evals must stay offline and deterministic.

**Choice:** `evals/agent_routing.py` scores each agent for a question with a lexical score (lower-cased token overlap, stop-words removed, weights: description ×2, "When you enter" ×1, "When not to enter" −1) and ranks with a stable tie-break on name. Metrics: top-1, top-3, per-family confusion, protected-role misroutes (critic/referee/verifier). Baseline = same scorer over the pre-change roster with golden labels mapped through aliases; stored as SDD evidence.

**Rationale:** Measures what the gate can control (distinct, trigger-rich descriptions) without provider calls.

**Alternatives Rejected:**
1. LLM judge routing — rejected: non-deterministic, provider call.
2. Only structural phase→agent tables — rejected: does not measure descriptions.

**Consequences:**
- Proxy ≠ host router; limitation stated in the report (`limitations` field).

---

### Decision 6: Mirror directories contain generated and hand files — gate scopes narrowly

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** `.claude/agents/` has `custom/`, `workflow/` subtrees and an untracked `README.md`.

**Choice:** Drift/orphan checks cover top-level `*.md` (`.claude/agents`, `.agents/agents`) and `*.toml` (`.codex/agents`) only. `README.md` at top level is reported as `non-agent file` (distinct message) and still fails until the owner resolves it; subdirectories are ignored. `sync` never deletes non-agent files.

**Rationale:** Never destroy owner content; keep the gate honest.

**Alternatives Rejected:**
1. Auto-delete orphans (current `sync_mirrors` does for `.md`) — rejected for non-agent names.

**Consequences:**
- The pre-existing `README.md` failure stays visible with a clearer message.

---

### Decision 7: Two waves, gates first

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** 25 rewrites + 27 removals + migrations are large.

**Choice:** Wave 1 lands renderer, gates, aliases, eval, parity fix and measures the routing **baseline** on the current 52. Wave 2 rewrites content and migrates names; every agent must pass lint before commit.

**Rationale:** Baseline must be captured before content changes; gates validate content as written.

**Alternatives Rejected:**
1. Content first — rejected: nothing to validate against; baseline lost.

**Consequences:**
- Wave 1 lint runs in report mode over the current 52 (they fail by design) and becomes blocking only in Wave 2.

---

## File Manifest

### Wave 1 — Infrastructure

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/agents.py` | Create | Source/render/eval contracts | @python-developer | None |
| 2 | `src/apiforge/dispatch/agent_source.py` | Create | Parse + schema + contract lint | @python-developer | 1 |
| 3 | `src/apiforge/dispatch/render.py` | Create | Claude/Devin/Codex renderers | @python-developer | 1, 2 |
| 4 | `src/apiforge/dispatch/mirrors.py` | Modify | Drift/sync via render; `.codex`; narrow orphans | (general) | 3 |
| 5 | `src/apiforge/rules/agent_aliases.yaml` | Create | 27 aliases | (general) | None |
| 6 | `src/apiforge/dispatch/aliases.py` | Create | Resolver + warning | @python-developer | 5 |
| 7 | `src/apiforge/dispatch/references.py` | Create | Referential integrity scan | @python-developer | 5, 6 |
| 8 | `src/apiforge/runtime/registry.py`, `application/next_step.py`, playbook loader, runtime store/replay loader | Modify | Apply `resolve_agent` at name ingress | (general) | 6 |
| 9 | `src/apiforge/agentops/agent_audit.py` | Modify | `apiforge_tools` (+ `tools` fallback) | (general) | None |
| 10 | `src/apiforge/agentops/parity.py` | Modify | gpt-codex → `.codex/agents` | (general) | None |
| 11 | `src/apiforge/evals/agent_routing.py` | Create | Proxy-router eval | @python-developer | 1, 2, 6 |
| 12 | `evals/corpus/agent-routing/cases.json` | Create | 60–100 golden cases (derived) | (general) | 11 |
| 13 | CLI `agents render/lint/references`, `evals agent-routing` | Modify | Surfaces | @python-developer | 3, 7, 11 |
| 14 | `scripts/check_release.py` | Modify | Wire gates | (general) | 4, 7 |
| 15 | `docs/catalog-contract.md` | Modify | `AF-AGENT-CONTRACT-*`, `AF-AGENT-ALIAS-*`, `AF-AGENT-RENDER-*`, `AF-AGENT-REF-*` | @code-documenter | 2–7 |
| 16 | `tests/dispatch/test_render.py` | Create | AT-001..005 | @test-generator | 3, 4 |
| 17 | `tests/dispatch/test_agent_lint.py` | Create | AT-006, AT-007 | @test-generator | 2 |
| 18 | `tests/dispatch/test_aliases_references.py` | Create | AT-008..010, AT-015 | @test-generator | 6, 7, 8 |
| 19 | `tests/evals/test_agent_routing.py` | Create | AT-012, AT-013 | @test-generator | 11 |
| 20 | `tests/agentops/test_parity.py` (existing or new) | Modify | AT-014 | @test-generator | 10 |
| 21 | `docs/sdd/API_FORGE_AGENT_ROSTER/evidence/routing-baseline.json` | Create | Baseline on 52 | (general) | 11, 12 |

### Wave 2 — Content and migration

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 22 | `agents/<25 roster>.md` | Create/Modify | 9-section EN contracts, access, tier, `apiforge_tools`, `replaces` | @prompt-engineer (general fallback) | 2 |
| 23 | `agents/<27 absorbed>.md` | Delete | Absorbed | (general) | 5, 22 |
| 24 | `.claude/agents/*.md`, `.agents/agents/*.md`, `.codex/agents/*.toml` | Regenerate | `agents render` | (general) | 3, 22 |
| 25 | `src/apiforge/rules/{playbooks,catalog/routing,agent_profiles,agentic_runtime,routing,capability_matrix}.yaml` | Modify | New names | (general) | 22 |
| 26 | `src/apiforge/runtime/supervisor.py`, `runtime/review.py` | Modify | `api-orchestrator`, reviewer names | (general) | 22 |
| 27 | 11 test files + `evals/corpus/economy-replay/*.json`, `evals/skills/evals.json` | Modify | New names (stored-replay fixtures keep one old-name case to exercise aliases) | @test-generator | 25 |
| 28 | `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/integrations/API_FORGE_DEVIN*.md`, `.devin/agents/api-forge-reviewer.md` | Modify | Routing docs | @code-documenter | 22 |
| 29 | `docs/sdd/API_FORGE_AGENT_ROSTER/evidence/{routing-candidate.json, agentic-quality-baseline.json, baseline-justification.md, audit.json}` | Create | Evidence | (general) | all |
| 30 | `docs/sdd/API_FORGE_AGENT_ROSTER/*.md` | Create | SDD chain (`sdd classify` profile) | @code-documenter | all |

**Total Files:** ~30 manifest entries (~120 files incl. 75 generated mirrors, 27 deletions)

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1–3, 6, 7, 11, 13 | Typed pure modules following repo contracts |
| @test-generator | 16–20, 27 | AT-mapped tests |
| @code-documenter | 15, 28, 30 | Catalog, routing docs, SDD chain |
| @prompt-engineer | 22 | Agent contract writing (triggers, method, output) |
| (general) | 4, 5, 8–10, 12, 14, 21, 23–26, 29 | Wiring, YAML, renames |
| Reviewers | — | `api-adversarial-critic` reviews 5 sample bodies + routing report before Wave 2 merge; `api-verifier` checks gates |

---

## Code Patterns

### Pattern 1: Source frontmatter + body (target shape)

```markdown
---
name: api-contract-architect
description: >-
  Use when designing or reviewing an OpenAPI or gRPC contract before or while code serves it:
  resource shape, naming, pagination, idempotency, Problem Details, proto services and gateway
  projections. Not for published-contract breaking changes (→ api-governance-reviewer).
access: read-only
model_tier: deep
rule_areas: [CONTRACT, REST, GRPC]
executors: [af-inventory, af-extractor, af-judge, af-verifier, af-synthesizer]
apiforge_tools: [contract show, grpc gateway, model proto]
replaces: [api-grpc-contract-engineer, api-grpc-parser-engineer, api-grpc-gateway-engineer]
---

Follow `AGENT_PROTOCOL.md`.

## When you enter
## When not to enter
## Inputs
## Method
## Output
## Done when
## Refusal and escalation
## Permissions
## Executors
```

### Pattern 2: Codex renderer

```python
import json

from apiforge.contracts.agents import AgentSource

_SANDBOX = {"read-only": "read-only", "writer": "workspace-write"}
_EFFORT = {"fast": "medium", "deep": "high"}


def _multiline(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return f'"""\n{escaped}\n"""'


def render_codex(agent: AgentSource) -> bytes:
    lines = [
        f"name = {json.dumps(agent.name, ensure_ascii=False)}",
        f"description = {json.dumps(agent.description, ensure_ascii=False)}",
        f'sandbox_mode = "{_SANDBOX[agent.access]}"',
    ]
    if agent.model_tier:
        lines.append(f'model_reasoning_effort = "{_EFFORT[agent.model_tier]}"')
    lines.append(f"developer_instructions = {_multiline(agent.body)}")
    return ("\n".join(lines) + "\n").encode("utf-8")
```

### Pattern 3: Claude renderer

```python
import yaml

_TOOLS = {
    "read-only": "Read, Grep, Glob, Bash",
    "writer": "Read, Grep, Glob, Bash, Edit, Write",
}
_MODEL = {"fast": "sonnet", "deep": "opus"}


def render_claude(agent: AgentSource) -> bytes:
    head: dict[str, str] = {
        "name": agent.name,
        "description": agent.description,
        "tools": _TOOLS[agent.access],
    }
    if agent.model_tier:
        head["model"] = _MODEL[agent.model_tier]
    front = yaml.safe_dump(head, sort_keys=False, allow_unicode=True, width=10_000)
    return f"---\n{front}---\n\n{agent.body}\n".encode("utf-8")
```

### Pattern 4: Alias resolution

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AliasResolution:
    name: str
    alias_of: str | None

    @property
    def warning(self) -> str | None:
        if self.alias_of is None:
            return None
        return f"AF-AGENT-ALIAS-DEPRECATED: {self.alias_of} -> {self.name}"


def resolve_agent(name: str, aliases: dict[str, str]) -> AliasResolution:
    target = aliases.get(name)
    return AliasResolution(name=target, alias_of=name) if target else AliasResolution(name, None)
```

### Pattern 5: Routing case

```json
{"id": "R001", "question": "Is this change to POST /orders a breaking change for published clients?", "expected": "api-governance-reviewer", "family": "contract", "source": "tests/rules/test_routing.py"}
```

---

## Data Flow

```text
1. Author edits agents/<name>.md
   │
   ▼
2. apiforge agents lint → AF-AGENT-CONTRACT-* on violations
   │
   ▼
3. apiforge agents render → .claude/.agents/.codex regenerated (deterministic)
   │
   ▼
4. Release gate: drift + lint + references + audit (+ evals agent-routing in SDD verify)
   │
   ▼
5. Runtime/replay loads names → resolve_agent → canonical (+ deprecation warning)
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| Claude Code | Reads `.claude/agents/*.md` | None |
| Devin | Reads `.agents/agents/*.md` | None |
| Codex | Reads `.codex/agents/*.toml` | None |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | parse, lint, render, aliases, references, eval scorer | `tests/dispatch/*`, `tests/evals/test_agent_routing.py` | pytest (`--basetemp E:/afpt`) | AT-001..AT-010, AT-012, AT-013 |
| Contract | TOML via `tomllib`, Claude frontmatter via yaml, byte idempotence | `test_render.py` | pytest | 100% of 25 agents × 3 hosts |
| Integration | release gate on repo; `agents audit`; supervisor alias | `tests/scripts/test_check_release.py`, `tests/runtime/*` | pytest | AT-011, AT-014, AT-015 |
| Eval | routing baseline vs candidate | `evals agent-routing` | CLI | ≥ baseline, 0 protected-role misroutes |
| Regression | agentic-quality, economy-hardening | CLI | re-recorded baseline with justification |
| Full suite | once before ship | pytest | green except documented pre-existing orphan |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Invalid frontmatter / missing section / word budget / non-EN / bad description | `AF-AGENT-CONTRACT-*` with field + unlock | No |
| Writer without `write_scope`; duplicated `apiforge_tools` owner | `AF-AGENT-CONTRACT-ACCESS`, `AF-AGENT-CONTRACT-TOOL-OWNER` | No |
| Drift / orphan / non-agent file | Gate failure listing paths (`AF-AGENT-RENDER-DRIFT`) | No |
| Unknown agent reference | `AF-AGENT-REF-UNKNOWN` with file:line | No |
| Alias used | Warning `AF-AGENT-ALIAS-DEPRECATED` in payload | N/A |
| Alias target missing / alias cycle | `AF-AGENT-ALIAS-INVALID` at load | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `agent_aliases.yaml: deprecated_in` | str | `roster-v2` | Release in which aliases are removed |
| lint `min_words` / `max_words` | int | 250 / 600 | Body budget |
| lint `max_description_chars` | int | 300 | Router context budget |
| render `model_tier` map | dict | fast→sonnet/medium, deep→opus/high | Host projection |

---

## Security Considerations

- Read-only is the default; writers must declare `write_scope`, reflected in body and host projection.
- Codex `sandbox_mode` enforces; Claude `tools` narrows; Devin relies on body text (limitation documented).
- Renderer and gates are offline and never touch non-agent files.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | JSON payloads via existing CLI echo |
| Metrics | Routing eval top-1/top-3, per-family confusion |
| Audit | Alias warnings in run payloads; drift list in release gate |

---

## Pipeline Architecture (if applicable)

N/A.

---

## Build Order

```text
Wave 1:
  L0 contracts/agents.py, rules/agent_aliases.yaml
  L1 dispatch/agent_source.py, dispatch/aliases.py
  L2 dispatch/render.py, dispatch/references.py, evals/agent_routing.py
  L3 mirrors.py, ingress resolve_agent, audit/parity fixes, CLI, check_release
  L4 tests, catalog, cases.json, routing baseline on current 52 (lint report-only)
Wave 2:
  L5 25 agent sources (lint blocking) → render mirrors
  L6 delete 27 absorbed; migrate rules/code/tests/evals/docs
  L7 audit 25/25, routing candidate ≥ baseline, re-record agentic-quality with justification, full suite, sdd chain
```
No cycles: `dispatch/render` depends on `agent_source` only; `aliases` is a leaf used by loaders; `evals/agent_routing` depends on source + aliases.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_AGENT_ROSTER.md`
