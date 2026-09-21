# API Forge Agentic Layer Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The platform's identity layer — 10 coordinator profiles + 5 executor profiles under `agents/` with an `AGENT_PROTOCOL.md` contract, `playbook` as the dispatch floor (decomposition as data, works without subagents), and an economy ledger that measures `payload_bytes` per call so savings are proven, not claimed.

**Architecture:** Mirroring spark-forge: coordinators in `agents/*.md` declare `rule_areas`, `executors`, and a `## Não faz` boundary; executors in `agents/executors/*.md` own one phase-loop function each with `## Pressupõe`/`## Entrega` handoffs. `agents/playbooks.yaml` maps each coordinator to its ordered executor steps — `apiforge playbook <coordinator>` renders them, the only path on platforms that cannot dispatch. `_echo_json` records `{verb, detail_level, payload_bytes}` into `.apiforge/economy.jsonl`; `economy report` aggregates per verb/level and computes `detail_level_effect` — bytes, never tokens without a transcript (`tokens_unresolved`).

**Depends on:** plans 1–7 (all verbs, routing.yaml, catalog areas, detail_level).

## Global Constraints

- Coordinator names must equal the `recommended_agent` values in `routing.yaml` — the release gate cross-checks both directions.
- `playbook` reads `agents/playbooks.yaml`; it never invents a decomposition.
- Economy records bytes of the emitted payload (post-`detail_level` projection); refusals count too; measurement never breaks the call.
- Agent profiles carry prose boundaries, not enforcement — same honesty as spark-forge: dropping `tools:` is not a security boundary.

## Task 1: protocol + coordinators + executors

**Files:**
- Create: `AGENT_PROTOCOL.md` (10 rules adapted to api-forge)
- Create: `agents/<coordinator>.md` ×10, `agents/executors/<executor>.md` ×5

- [ ] Step 1: `AGENT_PROTOCOL.md` — case-first, next-step-before-agent, no number without `fact_id`, `rules lookup` over memory, sandbox-only builds, record executors used, report `unresolved`, confirm framework before citing, destructive → escalate, receipt = correspondence.
- [ ] Step 2: 10 coordinator files (frontmatter: name, description, `rule_areas`, `executors`; body: quando entra/fronteira de despacho, decomposition, `## Não faz`, `## Pressupõe`/`## Entrega`): `api-contract-architect`, `api-governance-reviewer`, `api-security-reviewer`, `api-performance-engineer`, `api-testing-strategist`, `api-reliability-engineer`, `aws-api-infra-reviewer`, `api-modernization-specialist`, `api-observability-engineer`, `api-dx-docs-reviewer`.
- [ ] Step 3: 5 executor files: `af-inventory` (discover/model/dump state), `af-extractor` (analyze verbs + collect), `af-judge` (judge/diff/next-step inputs), `af-verifier` (sandbox/worktree/evidence), `af-synthesizer` (report/rules/next-step/build).
- [ ] Step 4: commit.

## Task 2: `playbook` verb + playbooks.yaml

**Files:**
- Create: `agents/playbooks.yaml` — per coordinator, ordered steps `{executor, verb, purpose}` using real CLI verbs
- Modify: `src/apiforge/cli.py` (`playbook <name>`), `tests/e2e/test_playbook.py`

- [ ] Step 1: author playbooks (e.g. governance-reviewer: af-inventory discover → af-extractor analyze → af-judge judge → af-verifier evidence emit → af-synthesizer next-step).
- [ ] Step 2: `apiforge playbook <coordinator>` renders steps JSON; unknown name → `AF-PLAYBOOK-NOT-FOUND`.
- [ ] Step 3: tests — renders declared steps, coordinator names ⊆ routing agents; commit.

## Task 3: economy ledger + `economy report`

**Files:**
- Create: `src/apiforge/economy/__init__.py`, `src/apiforge/economy/ledger.py`
- Modify: `src/apiforge/cli.py` (record in `_echo_json`; `economy report [--root]`)
- Create: `tests/economy/test_ledger.py`, `tests/economy/test_report.py`

- [ ] Step 1: `ledger.py` — `record(root, entry)` appends JSONL `{verb, detail_level, payload_bytes}` to `.apiforge/economy.jsonl` (best-effort; a write failure records nothing, never breaks the call); `report(root)` aggregates `calls`, `payload_bytes`, `by_verb`, `by_level`, `detail_level_effect` (bytes summary vs normal for verbs seen at both levels), `tokens_unresolved: true` when no provider transcript exists.
- [ ] Step 2: `_echo_json` records after serialization; `economy report` prints the aggregate.
- [ ] Step 3: tests — bytes recorded per call, summary<normal delta reported, no transcript → `tokens_unresolved`; commit.

## Task 4: gate + docs

**Files:**
- Modify: `scripts/check_release.py` (coordinators ⊆/⊇ routing agents, executors exist, `AGENT_PROTOCOL.md` referenced by every profile, playbooks ⊆ coordinators, AF-ECONOMY/AF-PLAYBOOK parity), `docs/catalog-contract.md`, `README.md`, `AGENTS.md` pointer file

- [ ] Step 1: edits; gate PASS; commit.

## Final acceptance

- [ ] `apiforge playbook api-governance-reviewer` prints the executor sequence
- [ ] `apiforge economy report` shows recorded bytes per verb and `detail_level_effect`
- [ ] Every `agents/*.md` name equals a routing `recommended_agent`; every executor file exists
- [ ] pytest/ruff/mypy/`check_release.py` green
