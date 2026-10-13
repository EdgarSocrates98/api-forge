# API Forge MCP Server + Context Funnel Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete plan 9 — the MCP surface (`apiforge-mcp`, extra `[mcp]`) exposing the read/compose verbs with `detail_level`, and a **measured** context funnel showing what each stage of the case keeps and drops, in bytes.

**Architecture:** `src/apiforge/mcp/` holds a thin FastMCP layer: every tool calls an existing application service (never duplicating logic), applies `apply_detail_level`, and records `payload_bytes` to the economy ledger — the same accounting the CLI has. The `mcp` package is an optional extra; its absence is `AF-MCP-UNAVAILABLE` with the unlock (`pip install apiforge[mcp]`). The funnel verb `context funnel --case <dir>` measures byte sizes at each persisted stage (api-ir → facts → findings → summary projection) — the funnel is reported, not asserted.

**Bounded decision (recorded):** the first MCP slice exposes **read/compose** verbs only — `discover`, `analyze`, `judge`, `model build`, `model api-gateway`, `diff contract`, `next-step`, `rules list`, `rules lookup`, `playbook`, `economy report`, `context funnel`. Mutating verbs (`build endpoint`, sandbox/worktree) stay CLI-only until policy-gating through MCP is designed.

## Task 1: `apiforge/mcp/` server + `[mcp]` extra

**Files:**
- Create: `src/apiforge/mcp/__init__.py`, `src/apiforge/mcp/tools.py` (shared call helper), `src/apiforge/mcp/server.py` (FastMCP wiring), `src/apiforge/mcp/main.py` (entry point, lazy import)
- Modify: `pyproject.toml` (`[project.optional-dependencies] mcp`, `apiforge-mcp` script)
- Create: `tests/mcp/test_tools.py` (tools work without the SDK: the wrapper layer is importable standalone; server import skipped when `mcp` absent)

- [ ] Step 1: `tools.py` — plain functions `discover(project, detail_level)` … `context_funnel(case_dir, detail_level)` returning projected dicts + recording economy entries (`verb` = `mcp:<name>`).
- [ ] Step 2: `server.py` — `build_server()` registers each tool on `FastMCP("apiforge")` with docstrings; lazily imports `mcp`.
- [ ] Step 3: `main.py` — `main()` imports `build_server`; `ImportError` → `AF-MCP-UNAVAILABLE` + unlock, exit 2. `pyproject` extra + script.
- [ ] Step 4: tests + commit.

## Task 2: `context funnel` verb

**Files:**
- Create: `src/apiforge/application/funnel.py`
- Modify: `src/apiforge/cli.py` (`context` group), `tests/e2e/test_funnel.py`

- [ ] Step 1: `measure_funnel(case_dir)` → `{"stages": [{stage, bytes}], "reduction": {...}, "diagnostics": []}`; missing case dir → `AF-INPUT-NOT-FOUND`; missing artifact → named diagnostic, not failure. `findings_summary` = `apply_detail_level(findings, "summary")` re-serialized.
- [ ] Step 2: CLI `context funnel --case <dir>` + MCP tool.
- [ ] Step 3: tests + commit.

## Task 3: gate + docs

**Files:**
- Modify: `scripts/check_release.py` (mcp import confined to `apiforge/mcp/`, `AF-MCP`/`AF-FUNNEL` parity), `docs/catalog-contract.md`, `README.md`, threat model row

- [ ] Step 1: edits; gate PASS; commit.

## Final acceptance

- [ ] `apiforge-mcp` entry point exists; without extra → `AF-MCP-UNAVAILABLE` with unlock
- [ ] Every MCP tool carries `detail_level` and records economy bytes
- [ ] `context funnel` reports measured stage bytes on the acceptance case
- [ ] pytest/ruff/mypy/`check_release.py` green
