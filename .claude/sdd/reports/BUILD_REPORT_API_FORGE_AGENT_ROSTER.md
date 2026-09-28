# BUILD REPORT: API Forge Agent Roster — Consolidate + Enrich, Host-Neutral

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENT_ROSTER |
| **Date** | 2026-09-28 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_AGENT_ROSTER.md](../features/DEFINE_API_FORGE_AGENT_ROSTER.md) |
| **DESIGN** | [DESIGN_API_FORGE_AGENT_ROSTER.md](../features/DESIGN_API_FORGE_AGENT_ROSTER.md) |
| **Status** | Complete |
| **Branch** | `sdd/agent-roster` (wave 1 `ecbc870`; wave 2 + critic fixes uncommitted at report time) |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 30/30 manifest entries |
| **Agents** | 52 → 25 (33 absorbed, aliased) |
| **Generated mirrors** | 75 (25 × Claude/Devin/Codex) |
| **Tests Passing** | targeted 483 passed / 1 skipped; full suite 1311 passed, 1 failed (pre-existing orphan README) |
| **Agents Used** | direct build + `api-adversarial-critic` review + 2 independent holdout authors (Haiku, Sonnet) |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1–3 | contracts, source parser + lint, renderer | (direct) | ✅ | Legacy sources mirror verbatim: zero drift on 156 files before content change |
| 4 | mirrors via render; `.codex`; non-agent files never deleted | (direct) | ✅ | README reported as `(non-agent file)` |
| 5–8 | aliases table + resolver + references gate + ingress wiring | (direct) | ✅ | Registry, profiles, next-step, dispatch, playbook CLI/MCP |
| 9–10 | audit reads `apiforge_tools`; parity gpt-codex → `.codex/agents` | (direct) | ✅ | |
| 11–13 | routing eval + 75 golden cases + CLI | (direct) | ✅ | Cases committed in wave 1 before any rewrite |
| 14–15 | release gate + catalog | (direct) | ✅ | drift, references, lint, audit blocking |
| 16–21 | wave 1 tests + baseline evidence | (direct) | ✅ | |
| 22 | 25 agents rewritten (EN, 9 sections) | (direct) | ✅ | 347–437 words each |
| 23–24 | 33 files removed; mirrors regenerated | (direct) | ✅ | |
| 25–27 | rules, supervisor, tests, docs migrated; playbooks merged | (direct) | ✅ | |
| 28–30 | docs, evidence, SDD chain | (direct) | ✅ | `sdd check` ok |
| review | adversarial review | api-adversarial-critic | ✅ | fix-first → fixes applied (below) |

---

## Verification Results

- `ruff check` / `ruff format --check`: clean (836 files). `mypy src`: no issues (459 files).
- `agents lint`: 25/25, no findings (tools exist in CLI, playbooks coherent). `agents audit`: 25 keep, 0 merge-candidate (was 8/52).
- `agents references`: ok. Render drift: none except pre-existing non-agent README.
- Routing golden (75): top-1 0.7333 → 0.9733, top-3 0.92 → 1.0, protected misroutes 5 → 0; leakage_4gram 0.2533.
- Routing independent holdout (80, two other models, labels from names only, leakage 0): top-1 0.2875 → 0.4625, top-3 0.4875 → 0.65, protected misroutes 13 → 9.
- `evals agentic-quality --baseline <economy baseline>`: passed, accuracy 1.0 on all profiles (no re-record needed). `evals economy-hardening`: passed.
- Host check: Claude Code reloaded the rendered agents with projected tools.

---

## Issues Encountered

| # | Issue | Resolution |
|---|-------|------------|
| 1 | DEFINE counted 27 aliases | Correct count is 33 (52 − 19 kept); table and tests use 33 |
| 2 | Reference gate flagged skill names `api-forge-*` and fictitious test names | Pattern excludes `api-forge-`; tests build fake names at runtime |
| 3 | `contract list/show` are API Forge's own contracts, not the user's API | DX owns `contract-intel twin` (offline consumer sandbox) instead |
| 4 | Critic: golden gain confounded (PT baseline, 25% 4-gram leakage, same author) | Added leakage metric and 80-case independent holdout; reported both |
| 5 | Critic: read-only agents owning state-writing commands | New `state-writer` access (governance, ops, verifier, critic, referee) |
| 6 | Critic: fake/nonexistent tools (`model rds`, `perf memory`) and ownership mismatches | Lint validates tools against the Typer tree; ownership corrected |
| 7 | Critic: playbooks used undeclared executors and nonexistent verbs | Lint checks playbooks; `observability verify`/`debate status` removed; executors declared |
| 8 | Haiku holdout author returned summaries instead of JSON | Asked it to write a file; added a Sonnet holdout; both kept |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|--------------------|-------|-----------|
| 1 | Delegate file writing | specialists vs direct | Direct | Cross-cutting contracts; consistency across 25 agents |
| 2 | Wave 1 behaviour for 52 legacy sources | force new schema vs legacy passthrough | Legacy passthrough | Zero drift, incremental migration |
| 3 | Alias table in wave 1 | absent vs inactive | Inactive, published | Baseline eval needs the mapping before activation |
| 4 | Uniqueness | new runtime capabilities vs owned commands | Owned real commands | Runtime routing unchanged; honest ownership validated by lint |
| 5 | Agents whose commands persist state | read-only vs writer vs new level | `state-writer` | Codex needs write sandbox; Claude still gets no Edit/Write |
| 6 | agentic-quality baseline | re-record vs keep | Keep | Passes unchanged against the previous baseline |
| 7 | `agents render` command | new command vs extend sync/check | Extend `agents sync|check` | Existing surface; fewer commands |
| 8 | Language-fair old baseline | translate 38 descriptions vs independent holdout | Independent holdout | Translation would inject the author's wording into the baseline |
| 9 | Holdout authorship | owner vs other models | Other models, names only | Owner time; no access to agent text |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| 33 aliases instead of 27 | Arithmetic error in DEFINE | None |
| Access gained `state-writer` | Critic finding | Three-level permission model |
| Lint also validates tools and playbooks | Critic finding | Stronger gate |
| agentic-quality baseline kept | Passed unchanged | Less churn |
| No `agents render` command | Existing `sync/check` extended | None |

---

## Unresolved

- Claude `Bash` is not narrowed per `apiforge` verb; Devin enforces permissions only through body text.
- The lexical proxy router is weak in absolute terms (holdout top-1 0.46); a host-router eval would need model calls.
- Holdout labels were assigned from agent names only; some labels may be debatable.
- `.claude/agents/README.md` (pre-existing, untracked) keeps the release gate red until the owner resolves it.

---

## Next Step

`/ship .claude/sdd/features/DEFINE_API_FORGE_AGENT_ROSTER.md`
