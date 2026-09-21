# API Forge Catalog Knowledge Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Populate the six skeletal catalog areas with real API-engineering rules and expose them through a `rules` CLI group, so coordinators have a knowledge base to cite — every finding/report references a `rule_id` traceable to a dated source.

**Scope:** `rest`, `security`, `testing`, `perf`, `breaking`, `gateway` yaml files get 6–8 knowledge rules each under the closed schema (id, title, severity, rationale, remediation, reference, runtime_scope). Knowledge rules guide agents and future executable judges; they are not refusal codes. `rules lookup <id>` / `rules list [--area]` read the catalog.

**Constraint:** `_check_rule_coverage` requires every `rule_id` in the test corpus — one test enumerates the expected rule set (also locking the catalog surface). `routing.yaml` areas must stay consistent with `load_areas()`.

## Task 1: author the six areas + rules verbs + coverage test

- [ ] Step 1: author `rest.yaml` (AF-REST-*: plural resource nouns, method semantics, status discipline, pagination, idempotency, Problem Details, versioning), `security.yaml` (AF-SEC-*: OWASP API Top 10 2023 — BOLA, auth, object-property authz, rate limiting, BFLA, SSRF, inventory), `testing.yaml` (AF-TEST-*: contract testing, schema validation, fuzz, mutation, load, chaos), `perf.yaml` (AF-PERF-*: pagination required, payload bounds, caching/ETag, compression, timeouts before retries, N+1), `breaking.yaml` (AF-BREAK-*: removal is breaking, type change is breaking, required-tightening, deprecation headers, sunset policy), `gateway.yaml` (AF-GW-*: no NONE authz on prod methods, throttling, access logs, WAF, cache invalidation, stage isolation).
- [ ] Step 2: `rules` CLI group: `rules list [--area]`, `rules lookup <id>` — reads catalog only.
- [ ] Step 3: `tests/rules/test_catalog_knowledge.py` enumerates every rule id (satisfies the coverage gate and locks the surface) + asserts severities/rationale/remediation non-empty and `reference` present.
- [ ] Step 4: full gate + suite; commit.

## Final acceptance

- [ ] `apiforge rules lookup AF-SEC-001` prints the OWASP rule
- [ ] `python scripts/check_release.py` PASS (coverage, catalog schema, routing ⊆ areas)
