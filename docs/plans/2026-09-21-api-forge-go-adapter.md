# API Forge Go Adapter Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the Go language adapter — `extract_go` via tree-sitter-go — with an `orders-go` parity lab proving the same API-IR and judge rules work unchanged for Go services.

**Architecture:** The `CodeInventory` contract (plan 3 task 4) is consumed as-is: `extract_go` parses `*.go` files with tree-sitter, never executes Go, never requires `go build`/modules. Recognized route shapes: `net/http` (`mux.HandleFunc("GET /x", h)`, `mux.Handle("/x", h)`, `http.HandleFunc`), `chi` (`r.Get("/x", h)`, `r.Route("/prefix", sub)`), `gin`/`echo` (`router.GET("/x", h)`). Non-literal path arguments emit `AF-GO-UNRESOLVED-ROUTE`; parse errors emit `AF-GO-PARSE`. Every scanned file contributes to `input_hashes`.

**Tech Stack:** tree-sitter-go pinned `>=0.23.4,<0.24`.

**Spec:** `docs/specs/2026-09-21-api-forge-agentic-platform.md` §8/§9 — delivers the Go half of sequence item 3.

**Depends on:** plan 3 (`CodeInventory`, `apply_detail_level`, `--framework` dispatch).

## Global Constraints

- Same discipline as the Spring adapter: literal-only resolution, named diagnostics, `input_hashes` covers every scanned file, extractor never touches a toolchain.
- `judge.py` UNCERTAIN_CODES gains the `AF-GO-*` codes so absence claims degrade to `unresolved` identically.
- Parity lab mirrors the defect shape of `orders-fastapi`/`orders-spring`.
- Production modules <300 lines; TDD; one commit per task.

## Task 1: `extract_go` adapter

**Files:**
- Create: `src/apiforge/adapters/go/__init__.py`, `src/apiforge/adapters/go/scan.py`, `src/apiforge/adapters/go/extractor.py`
- Modify: `pyproject.toml` (dep pin)
- Create: `tests/adapters/go/test_go_extractor.py`, fixture `tests/fixtures/go_orders/`

- [ ] Step 1: pin `tree-sitter-go>=0.23.4,<0.24`, `uv sync`.
- [ ] Step 2: fixture `go_orders` — chi router with `r.Route("/v1", …)`, `r.Get/Post/Delete`, one `mux.HandleFunc` net/http route, one `gin.GET`, one non-literal path var, one `.go` file with a syntax error.
- [ ] Step 3: RED test — routes extracted with method/path/handler/line; non-literal → `AF-GO-UNRESOLVED-ROUTE`; broken file → `AF-GO-PARSE` + hashed anyway.
- [ ] Step 4: `scan.py` (AST→RouteRecord/unresolved per file: call_expression shapes for `HandleFunc|Handle|Get|Post|Put|Delete|Patch|Route`, receiver-qualified literals, `chi`-style verb methods); `extractor.py` (discovery, hashing, `CodeInventory`).
- [ ] Step 5: GREEN + lint/mypy; commit.

## Task 2: `orders-go` lab + `--framework go` + parity

**Files:**
- Create: `tests/labs/orders-go/` (mirrors defect shape: `/v1` prefix vs contract `/orders`, duplicate POST, dynamic route, `/secret`)
- Modify: `src/apiforge/application/analyze.py` (`_EXTRACTORS["go"]`, `_detect_framework` counts `.go`)
- Modify: `src/apiforge/rules/judge.py` (UNCERTAIN_CODES += `AF-GO-*`)
- Modify: `src/apiforge/cli.py` (framework help text)
- Create/extend: `tests/e2e/test_go_parity.py`

- [ ] Step 1: lab files; RED parity test (same `(rule_id, severity, status)` tuples as fastapi).
- [ ] Step 2: wire extractor + detect (`java>py>go` counts; none → `AF-INPUT-FRAMEWORK-UNKNOWN` unchanged).
- [ ] Step 3: GREEN; commit.

## Task 3: docs + gate extension

**Files:**
- Modify: `docs/catalog-contract.md` (AF-GO-* section)
- Modify: `docs/security/threat-model-mvp.md` (Go row)
- Modify: `README.md` (Go adapter line, `--framework go`)
- Modify: `scripts/check_release.py` (parity prefix `AF-GO`, lab presence, tree-sitter import confinement widened to `adapters/spring|adapters/go`)

- [ ] Step 1: edits; gate PASS; commit.

## Final acceptance

- [ ] `pytest -q` green; ruff/format/mypy clean; `python scripts/check_release.py` PASS
- [ ] `apiforge analyze --contract orders-v1.yaml --project tests/labs/orders-go --framework go` exits 0
