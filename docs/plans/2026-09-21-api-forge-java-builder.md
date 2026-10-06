# API Forge Java Builder Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** First mutation verb — `build endpoint` synthesizes a Spring Boot endpoint skeleton (controller + DTO records) from an OpenAPI operation, emits it as a unified diff, proves it in the copy sandbox, and only promotes into a git worktree when policy gates are satisfied. The main tree is never touched.

**Architecture:** `apiforge.build.java` maps an operation to deterministic Java sources (new files only — never edits existing files); `apiforge.build.service` orchestrates `policy decide` → synthesize → `sandbox_apply` → optional `worktree` promotion → evidence receipt binding diff sha256 + sandbox id + contract sha256 + policy decision. The sandbox analyzer is `extract_spring`+`judge_api_model` against the same contract, so the delta shows the new route resolving its `AF-CONTRACT-001`.

**Tech Stack:** existing plan-1/2 primitives; no new dependencies.

**Spec:** `docs/specs/2026-09-21-api-forge-agentic-platform.md` — sequence item 7 (builder muta código; Java é o primeiro alvo de geração).

**Depends on:** plans 1–5 (`sandbox_apply`, `worktree_create`, `decide`/`DEFAULT_POLICY`, `load_openapi`, `extract_spring`, `judge_api_model`).

## Global Constraints

- Generated code is new files only under `src/main/java/com/apiforge/generated/` — a build never edits an existing file; target-present → `AF-BUILD-TARGET-EXISTS`.
- `build.endpoint` is `local_reversible` (sandbox evaluation); promotion is `sensitive` and requires the policy gates' evidence — `--approve` records the approval evidence kind, never a boolean bypass.
- Type mapping is bounded and deterministic: `string→String`, `integer→Long`, `number→BigDecimal`, `boolean→Boolean`, `array<X>→List<X>`, `$ref→record`, unref'd `object→Map<String,Object>`. Unknown/absent schema → `AF-BUILD-SCHEMA-MISSING`, never a guessed type.
- The diff itself passes through `sandbox_apply`'s own refusals (path escape, target missing).
- Receipt proves correspondence: hashes of contract, diff, sandbox report — never authorship.

## Task 1: Java synthesizer

**Files:**
- Create: `src/apiforge/build/__init__.py`, `src/apiforge/build/java.py`, `src/apiforge/build/diff.py`
- Create: `tests/build/test_java.py`, `tests/build/test_diff.py`

- [ ] Step 1: `java.py` — `operation_to_sources(document, operation_id) -> dict[relpath, content]`:
  `generated/<Op>Controller.java` (`@RestController`, `@<Method>Mapping("<path>")`, `ResponseEntity<Dto>` return, `@PathVariable` for `{x}` segments, `@RequestBody` when requestBody required) + `generated/dto/<Schema>.java` records for requestBody/response `$ref`s (bounded scalar mapping above). Missing operation → `AF-BUILD-OP-MISSING`; absent component schema → `AF-BUILD-SCHEMA-MISSING`.
- [ ] Step 2: `diff.py` — `sources_to_diff(sources) -> str` emitting `--- /dev/null`/`+++ b/<path>` new-file patches; must round-trip through `parse_unified_diff`.
- [ ] Step 3: RED→GREEN tests; commit.

## Task 2: build service + sandbox evaluation

**Files:**
- Create: `src/apiforge/build/service.py`
- Create: `tests/build/test_service.py`

- [ ] Step 1: `build_endpoint(contract, project, operation_id, promote=None, approve=False) -> BuildReport`: policy `decide` on `build.endpoint` (local_reversible); synthesize; refuse `AF-BUILD-TARGET-EXISTS` on collision; `sandbox_apply(project, diff, analyze=_judge_side)` where `_judge_side(root)` runs `extract_spring`+`judge_api_model`→findings; report = diff sha256, sandbox id, files, finding delta, decision.
- [ ] Step 2: tests — orders-v1.yaml `getOrder`-shaped op against an empty maven-layout project: report.applied, delta shows a new `code.route` covering the operation (via a `resolved`/`new` finding list), deterministic receipt.
- [ ] Step 3: commit.

## Task 3: CLI + worktree promotion + docs/gate

**Files:**
- Modify: `src/apiforge/cli.py` (`build endpoint`), `README.md`, `docs/catalog-contract.md` (AF-BUILD-*), threat model (mutation boundary row), `scripts/check_release.py` (AF-BUILD parity)
- Create: `tests/e2e/test_build.py`

- [ ] Step 1: `apiforge build endpoint --contract --operation-id --project [--write-diff f.diff] [--into-worktree NAME --approve]`.
- [ ] Step 2: promotion: `decide(worktree.apply, sensitive)` → gates satisfied only with `--approve` (records `approval` evidence in report); `worktree_create` + write the new files into the worktree path; main tree untouched.
- [ ] Step 3: docs + gate; commit.

## Final acceptance

- [ ] `build endpoint` on the orders contract emits a diff that `sandbox apply` accepts and the delta shows the new route
- [ ] `--into-worktree` without `--approve` is gated (named refusal), with `--approve` lands files only in the worktree
- [ ] pytest/ruff/mypy/`check_release.py` green
