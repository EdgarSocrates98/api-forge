# API Forge AWS Collect/Analyze Slice Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** First cloud capability — `collect api-gateway` fetches AWS API Gateway configuration into versioned artifact dumps, and `analyze api-gateway` reads those dumps offline into facts. The core stays offline: boto3 lives only in `collectors/` behind an injected client, so tests never touch AWS.

**Architecture:** `apiforge.collectors.apigateway.collect(client, api_id, stage, out_dir, now)` writes `rest-api.json`, `resources.json`, `stages.json`, `authorizers.json` + `manifest.json` (api id, stage, `--now` timestamp — the only clock). `apiforge.adapters.apigateway.extract(dump_dir)` reads the dump offline → `aws.apigateway.*` facts (resource/method/auth/throttling/caching/logging) + named diagnostics for missing or partial dumps. No judge integration in this slice — facts are the evidence layer; rules arrive with the catalog population plan.

**Tech Stack:** boto3 as an optional `aws` extra (`boto3>=1.34,<2`), never imported outside `collectors/` — the release gate enforces the boundary.

**Spec:** `docs/specs/2026-09-21-api-forge-agentic-platform.md` — sequence item 6.

**Depends on:** plans 1–4 (Fact/SourceRef/Diagnostic/CodeInventory contract, CLI conventions, gate).

## Global Constraints

- `collect *` is the only family that touches AWS; boto3 import confined to `src/apiforge/collectors/` — enforced by the release gate, same mechanism as tree-sitter.
- `analyze api-gateway` must work on a bare dump directory with no AWS credentials and no network.
- `--now` is the only timestamp source; absent → manifest records `collected_at: null`, never wall-clock.
- Every missing/invalid dump file degrades to a named diagnostic (`AF-GW-DUMP-MISSING`, `AF-GW-DUMP-INVALID`), never a guess.
- The collector refuses to write outside `out_dir` (same path discipline as `save_case`).

## Task 1: collector + dump layout

**Files:**
- Create: `src/apiforge/collectors/__init__.py`, `src/apiforge/collectors/apigateway.py`, `src/apiforge/collectors/manifest.py`
- Modify: `pyproject.toml` (`aws` extra), `src/apiforge/cli.py` (`collect api-gateway` command)
- Create: `tests/collectors/test_apigateway.py` (fake injected client)

- [ ] Step 1: `manifest.py` — `CollectManifest` (api_id, stage, collected_at|None, artifact list with sha256, tool version); `write_artifact(out_dir, name, payload)` → sha256-recorded JSON files.
- [ ] Step 2: `apigateway.py` — `collect(client, api_id, out_dir, now)`: `get_rest_api`, `get_resources` (paginated `items`), `get_stages`, `get_authorizers`; boto3 errors → `AF-COLLECT-AWS` refusal; injected client so tests never need AWS.
- [ ] Step 3: CLI `collect api-gateway --api-id --out --now` — builds `boto3.client("apigateway")` lazily inside the command; exit codes consistent.
- [ ] Step 4: tests with a stub client (dict-returning `get_rest_api` etc.); commit.

## Task 2: `analyze api-gateway` extractor

**Files:**
- Create: `src/apiforge/adapters/apigateway/__init__.py`, `src/apiforge/adapters/apigateway/extract.py`
- Create: `tests/fixtures/aws/apigateway/` (hand-authored dump matching Task 1 layout)
- Create: `tests/adapters/apigateway/test_extract.py`

- [ ] Step 1: fixture dump — rest api, resources with `resourceMethods` (incl. `authorizationType: NONE` vs `AWS_IAM`/`CUSTOM`, `apiKeyRequired`), two stages (one with throttling+methodSettings+accessLogSettings, one bare), one `NONE`-type authorizer gap.
- [ ] Step 2: `extract(dump_dir)` → facts `aws.apigateway.api`, `aws.apigateway.resource` (path + methods with auth/apiKey), `aws.apigateway.stage` (throttling/cache/logging settings); missing files → `AF-GW-DUMP-MISSING`, malformed → `AF-GW-DUMP-INVALID`; every dump file hashed into `input_hashes`.
- [ ] Step 3: tests — facts, per-method auth attrs, diagnostics for removed dump file; commit.

## Task 3: CLI + docs + gate

**Files:**
- Modify: `src/apiforge/cli.py` (`analyze api-gateway --path`), `README.md`, `docs/catalog-contract.md` (AF-GW-*/AF-COLLECT-* codes), threat model (AWS boundary row), `scripts/check_release.py` (boto3 confinement + code parity)

- [ ] Step 1: edits; `check_release.py` PASS; full suite green; commit.

## Final acceptance

- [ ] `apiforge analyze api-gateway --path tests/fixtures/aws/apigateway` exits 0 offline
- [ ] `grep -r boto3 src/apiforge` matches only under `collectors/` (gate-enforced)
- [ ] pytest/ruff/mypy/`check_release.py` all green
