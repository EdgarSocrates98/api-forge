# BRAINSTORM: API Forge Agent Roster — Consolidate + Enrich, Host-Neutral

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENT_ROSTER |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent (+ Multi-Agent Systems Architect review) |
| **Status** | ✅ Complete (Defined) |
| **Branch** | `sdd/agent-roster` (stacked on `sdd/new-forge` @ 9cbe0fe) |

---

## Initial Idea

**Raw Input:** "quero que os agents sejam o melhores possível, que sigam as melhores boas práticas e que garantam a maior qualidade e potência do projeto inteiro independente de claude, devin ou codex"

**Context Gathered:**
- 52 coordinators in `agents/*.md` (source of truth), mirrored byte-identical to `.claude/agents/` and `.agents/agents/` by `dispatch/mirrors.py` (`sync_mirrors`, `mirror_drift`, release gate `scripts/check_release.py:373`); `.codex/agents/*.toml` added manually in 9cbe0fe, not in sync/gate.
- 28/52 bodies < 35 words (stubs: "Siga `AGENT_PROTOCOL.md`" + one sentence); average 95 words; ~6 rich bodies (`api-security-reviewer`, `api-governance-reviewer` 323 words, `api-data-access-architect` 244).
- `apiforge agents audit` → 8 keep / 44 merge-candidate (no unique capability/tool/validator/decision role declared). Report-only; merge is a human decision.
- Mixed PT/EN descriptions; weak descriptions do not route (e.g. "Python, Go and Java generated artifact specialist.").
- `agentops/parity.py:9` maps `gpt-codex` → `.agents/agents`; Codex reads `.codex/agents` (bug).
- Name references outside mirrors: `rules/playbooks.yaml` (51 distinct names), `rules/catalog/routing.yaml` (18), `rules/agent_profiles.yaml` (8), `rules/agentic_runtime.yaml` (8), `rules/routing.yaml` (2), `rules/capability_matrix.yaml` (1); hardcoded `api-agentic-orchestrator` in `runtime/supervisor.py` (228, 649, 743, 999, 1120, 1513); `runtime/review.py:78`; 11 test files; `evals/corpus/economy-replay/*.json` (4), `evals/skills/evals.json`; docs (`AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/README*`, `docs/integrations/API_FORGE_DEVIN*`, `.devin/agents/api-forge-reviewer.md`); persisted `.apiforge/**/routing.json|replay.json|events.jsonl`.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `agents/`, `src/apiforge/dispatch/` (renderer, mirrors, aliases), `src/apiforge/agentops/` (audit, parity), `src/apiforge/rules/*.yaml`, `scripts/check_release.py`, `evals/corpus/agent-routing/` | Renderer generalizes `sync_mirrors` |
| Relevant KB Domains | agentspec: `anti-patterns`, `component-model`; project skills: `api-forge-context`, `api-forge-sdd`, `api-forge-verification` | Agent design, SDD gates, verification independence |
| IaC Patterns | N/A | Local-only |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Strategy for roster? | Consolidate + enrich | 52 → 25 agents with full contracts |
| 2 | Process? | Full SDD | brainstorm → define → design → build → ship with critic |
| 3 | Done criterion? | Audit + routing + parity | 25/25 `keep`, routing eval ≥ baseline, 3-host parity gate, contract lint |
| 4 | Old names? | Aliases with deprecation | `rules/agent_aliases.yaml`; dispatch/replay resolve + warn; removal next release |
| 5 | Permissions? | Declare in source, project per host | `access`/`write_scope` → Claude `tools`, Codex `sandbox_mode`; reviewers read-only |
| 6 | Routing ground truth? | Derive from existing cases | Golden from routing/playbook/next_step tests + "when you enter" text; critic reviews; owner spot-checks |
| 7 | Approach? | A (single source + renderer + 25, two build waves) | Infra/gates first, content second |
| 8 | Language? | English | All agent descriptions/bodies EN; AF codes, commands, user docs unchanged |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `agents/*.md` | 52 | Current coordinators; 6 rich bodies are style references |
| Output examples | `agents/api-security-reviewer.md`, `api-governance-reviewer.md`, `api-data-access-architect.md` | 3 | Best current bodies → template seeds |
| Ground truth | `tests/rules/test_routing.py`, `tests/runtime/test_routing.py`, `tests/e2e/test_playbook.py`, `tests/e2e/test_next_step.py`, `rules/catalog/routing.yaml` | ~5 sources | Derive 60–100 question → agent golden cases |
| Related code | `dispatch/mirrors.py`, `agentops/agent_audit.py`, `agentops/parity.py`, `scripts/check_release.py` | 4 | Extend, don't replace |

**How samples will be used:**
- Rich bodies seed the 9-section template and tone.
- Routing golden = regression oracle for consolidation (old question must land on the absorbing agent).
- Existing tests become referential-integrity fixtures.

---

## Approaches Explored

### Approach A: Single source + renderer + 25-agent roster, two build waves ⭐ Recommended

**Description:** Host-neutral frontmatter in `agents/*.md`; deterministic renderer to Claude/Devin/Codex; gates (render-drift incl. `.codex`, contract lint, referential integrity, audit, routing eval); aliases; then rewrite 25 agents and migrate references.

**Pros:**
- Content is validated by gates as it is written.
- One source, three hosts, least privilege per host.
- Measurable DONE (25/25 keep, routing eval).

**Cons:**
- Large SDD; eval baseline re-record must be justified.

**Why Recommended:** Generalizes existing `sync_mirrors`/`mirror_drift` and `agents audit` (codebase pattern, conf. 0.80); specialist review converges.

---

### Approach B: Lean roster (~12) + skills

**Description:** One agent per decision; specialisms (gRPC, vendors) as skills.

**Pros:**
- Fewest agents, simplest routing.

**Cons:**
- Skills not portable uniformly across 3 hosts; specialism less actionable.

---

### Approach C: 25 agents, no renderer

**Description:** Rewrite roster; keep byte-identical md mirrors; `.codex` hand-maintained and checked.

**Pros:**
- Less code.

**Cons:**
- No per-host permission projection; `.codex` drift returns.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28, brainstorm session |
| **Reasoning** | Best quality with host independence; gates before content |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | 25-agent roster covering all 52 | Audit shows 44 indistinct; families collapse into domain owners | Keep 52 |
| 2 | Critic, referee, verifier stay separate | Independence is the contract (AGENT_PROTOCOL) | Merge review roles |
| 3 | Host-neutral frontmatter (`access`, `write_scope`, `model_tier`) | Project to Claude `tools`/`model`, Codex `sandbox_mode`/`model_reasoning_effort` | Host-specific sources |
| 4 | Mirror gate compares to `render(source, host)` | Byte-identical impossible once hosts diverge | Byte copy |
| 5 | Aliases for one release | Replays and user habits keep working | Hard break |
| 6 | English roster | Consistent routing across hosts/models | PT / mixed |
| 7 | 9-section body, 250–600 words, description ≤300 chars "Use when… Not for… (→ X)" | Routing trigger + explicit contract | Free form |
| 8 | Fix `parity.py` gpt-codex → `.codex/agents` | Existing bug | Leave |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Per-agent answer-quality golden eval | Owner chose audit + routing + parity | Yes |
| Rewriting `af-*` executors | Not dispatchable; outside problem | Yes |
| Family skills (gRPC, vendors) | Approach B rejected | Yes |
| Per-host concrete model IDs | Hosts change IDs; `model_tier` enough | Yes |
| Translating user docs to EN | Only agents change language | Yes |
| Alias removal | Next release | Yes |
| Rich Devin frontmatter | No Devin schema in repo; minimal is safe | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Scope in/out (YAGNI) | ✅ | "Sim, segue" | No |
| Flow, roster of 25, access, gates | ✅ | "Sim, gera o documento" | No |

---

## Proposed Roster (25)

| # | Agent | Absorbs | Access |
|---|-------|---------|--------|
| 1 | api-orchestrator | agentic-orchestrator, agentic-observability-engineer, grpc-agentic-engineer | writer (ledger) |
| 2 | api-planner | planner, runtime-migration-planner | writer (plans) |
| 3 | api-task-spec-reviewer | — | read-only |
| 4 | api-platform-selector | — | read-only |
| 5 | api-architecture-reviewer | — | read-only |
| 6 | api-infra-reviewer | terraform-reviewer, aws-api-infra-reviewer, drift-reconciliation-engineer | read-only |
| 7 | api-contract-architect | grpc-contract, grpc-parser, grpc-gateway | read-only |
| 8 | api-governance-reviewer | grpc-compatibility | read-only |
| 9 | api-codegen-engineer | grpc-codegen, grpc-toolchain | writer (worktree) |
| 10 | api-security-reviewer | grpc-security, observability-security | read-only |
| 11 | api-data-access-architect | relational-data-architect, analytical-data-architect | read-only |
| 12 | api-event-driven-architect | streaming-platform-architect | read-only |
| 13 | api-resilience-engineer | grpc-runtime, slo-reliability | read-only |
| 14 | api-performance-engineer | grpc-performance | read-only |
| 15 | api-load-capacity-engineer | load-test-engineer, capacity-engineer | writer (scenarios) |
| 16 | api-observability-engineer | instrumentation, grpc-observability, telemetry-normalization | read-only |
| 17 | api-observability-integration-engineer | observability-control-plane, vendor-integration, datadog, dynatrace | writer (projections) |
| 18 | api-test-strategist | — | read-only |
| 19 | api-dx-docs-reviewer | — | read-only |
| 20 | api-modernization-specialist | — | read-only |
| 21 | api-operations-engineer | — | read-only |
| 22 | api-verifier | verification-engineer, runtime-migration-verifier, platform-completion-reviewer | read-only |
| 23 | api-adversarial-critic | — | read-only |
| 24 | api-debate-referee | — | read-only |
| 25 | api-release-guardian | — | writer (release artifacts) |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
The 52 API Forge coordinators are mostly indistinguishable stubs (28 under 35 words, 44 flagged merge-candidate by the project's own audit), mix languages, carry no host-neutral permissions, and are mirrored to Codex outside any gate — so routing quality and agent behavior depend on the host rather than on the project.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Owner/maintainer | Cannot tell agents apart; audit says 44 are redundant |
| Host runtime (Claude/Devin/Codex router) | Weak descriptions → misrouting; no permission projection |
| Downstream reviewers (verifier/critic) | Agents lack explicit inputs/outputs/done criteria to check against |

### Success Criteria (Draft)
- [ ] `apiforge agents audit` → 25 agents, 25 `keep`, 0 merge-candidate.
- [ ] Every agent passes contract lint: 9 sections, 250–600 words, EN, description ≤300 chars with "Use when"/"Not for".
- [ ] Render-drift gate green for `.claude`, `.agents`, `.codex` (incl. orphans, TOML validity, access→tools/sandbox coherence).
- [ ] Referential integrity: 0 agent names in rules/code/tests/evals outside roster ∪ aliases.
- [ ] Routing eval golden (60–100 cases) accuracy ≥ pre-change baseline; every old-name case resolves to its absorbing agent.
- [ ] Replays with old names still run (alias + `AF-AGENT-ALIAS-DEPRECATED` warning).
- [ ] `parity.py` maps gpt-codex to `.codex/agents`.
- [ ] Full suite, `sdd check`, `evals economy-hardening`, `evals agentic-quality --baseline` (re-recorded with justification) green.

### Constraints Identified
- `agents/*.md` stays the single source; mirrors only generated.
- No provider SDK; no host API calls; offline render.
- AF-* codes with field/unlock, cataloged.
- Critic/referee/verifier independence preserved.
- Stacked branch on `sdd/new-forge`.

### Out of Scope (Confirmed)
- Answer-quality goldens per agent; executor rewrite; family skills; concrete model IDs; user-doc translation; alias removal; rich Devin schema.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 8 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 2 |
| Duration | 1 session |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_AGENT_ROSTER.md`
