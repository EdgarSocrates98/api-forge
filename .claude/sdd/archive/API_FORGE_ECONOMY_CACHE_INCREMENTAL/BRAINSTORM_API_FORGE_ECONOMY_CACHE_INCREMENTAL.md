# BRAINSTORM: API Forge Economy — Cache & Incremental Intelligence (Onda 2)

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_CACHE_INCREMENTAL |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** `prompt_evo_economy.md` — "entregar todo o restante do prompt, /agentspec por onda, commit por onda". Waves 0, 1 (`2cd00b5`) and 3 (`18c6bbd`) shipped. This cycle: Wave 2 — §21 incremental code intelligence, §22 delta-first, §23 dependency-aware invalidation, §24 multi-level cache, §25 freshness, §48–51 workspace/shared cache + content-addressable store.

**Context Gathered:**
- `index/cache.py::extract_cached` — whole-project extractor cache keyed `sha256(version|framework|source_digest)`; hit/miss recorded in `economy.jsonl`.
- `index/treehash.py::source_entries` — per-file `{path, sha256, bytes}` manifest already computed (basis for a file delta).
- `context/gateway/refs.py::CtxStore` — repo-local CAS `.apiforge/ctx/<sha256>`, hash re-verified on read.
- `context/gateway/levels.py::_graph` — **graph cache keyed by `case_id` only**: re-analysis with same case id but changed facts reuses a stale graph (latent freshness bug, §25).
- `graph/store.py` — per-node `sha256` over canonical `{id, kind, props}` → node-level diff between two graph snapshots is free.
- `graph/impact.py::assess_graph_impact` — reverse/forward traversal for dependents.
- `sandbox/worktree.py::_git` — precedent for read-only `git -C <root>` argv calls (no `shell=True`).
- Capsules are rebuilt from scratch on every call; `cache_hits` only counts ctx objects already present.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/cache/` (new), `contracts/cache.py`, `context/gateway/{levels,capsule}.py`, `context/delta.py`, `evals/cache.py`, CLI/MCP | Reuse gateway + graph store |
| Relevant KB Domains | pydantic, testing, python, anti-patterns | Versioned contracts, deterministic tests |
| IaC Patterns | N/A | Local-first, offline, no provider SDK |

---

## Discovery Questions & Answers

> User pre-approved the whole remaining program and asked for autonomous execution; answers derive from the prompt, shipped contracts and codebase evidence.

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Which cache layers ship now (§24 lists L1–L8)? | L1 parse, L2 graph, L3 impact, L4 capsule enforced; L5 knowledge, L6 routing, L7 validation declared in policy; L8 model-response declared **disabled** (no model answers exist in the offline core) | Single `CacheEntry/v1` + policy table; no fake layers |
| 2 | Is "incremental" real re-parsing per file? | No: extractors resolve cross-file. Incremental = file delta → changed graph nodes (node sha diff) → dependency-aware invalidation of downstream entries. Re-extraction stays whole-project but cached | Honest claim recorded in receipts (`reparse: full`, `invalidation: node`) |
| 3 | Where does the shared cache live (§50)? | Repo-local by default; opt-in shared tier via `APIFORGE_CACHE_HOME` / `--cache-home` (workspace or `~/.apiforge`). Objects are content-addressed and re-hashed on read, so sharing never trusts foreign bytes | Locality-first (§49) preserved |
| 4 | How does delta-first get the delta (§22)? | Read-only `git diff --name-status <base>..<head>` (argv, no shell) or explicit `--changed` list; maps files → graph nodes → impacted operations → capsule targets | New `DeltaSlice/v1`; hostless when no git (explicit `--changed`) |
| 5 | What proves it? | `evals cache` corpus on `economy_payments`: unchanged rebuild = 100% hit & byte-identical; model change invalidates only dependent capsules; unrelated change keeps hits; stale-critical never reused | Gates: `stale_reuse == 0`, precision/recall of invalidation |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/economy_payments/` | 1 fixture (FastAPI + Spring) | Payments/customers ops, models, tests |
| Output examples | `evals/corpus/economy/*.yaml` | 12 | Capsule targets reused as cache scenarios |
| Ground truth | `evals/corpus/economy-cache/*.yaml` (to create) | ~8 | mutation → expected invalidated/kept targets |
| Related code | `index/cache.py`, `gateway/refs.py`, `graph/store.py`, `graph/impact.py` | — | Integration points |

**How samples will be used:**

- Materialize fixture in tmp, analyze, build capsules (warm), apply a scripted file mutation, re-analyze, rebuild → compare hits/invalidations with ground truth.
- Unit tests for freshness decisions and git-delta parsing use synthetic inputs.

---

## Approaches Explored

### Approach A: Unified `CacheEntry/v1` store with dependency index ⭐ Recommended

**Description:** One `cache/` package: `CacheStore` (entries `<home>/cache/<layer>/<key>.json` + objects via CAS), `CacheEntry/v1` carrying `inputs_sha`, `source_sha`, `policy_sha`, `expertise_sha`, `deps` (graph node ids + file paths), `created_at`, `expires_at`; `freshness()` → `fresh|stale_harmless|stale_critical|invalidated` → `reuse|reuse_warn|recompute|invalidate` per layer policy (`rules/cache_policies.yaml`). Graph cache re-keyed by input digest; capsule cache (L4) keyed by target+budget+graph digest+policy digest; delta/invalidate walks reverse edges.

**Pros:** one contract for all layers; freshness generalized (§25); explicit, auditable invalidation; reuses CAS + node sha.
**Cons:** capsule re-key changes ledger `cache_hits` semantics (documented).

**Why Recommended:** codebase already has every primitive (node sha, CAS, impact traversal); confidence 0.90 (codebase pattern + prompt spec).

### Approach B: Per-layer ad-hoc caches

**Description:** Patch `_graph` key, add a capsule memo dict on disk, keep extractor cache as is.
**Pros:** smallest diff. **Cons:** no freshness model, no dependency invalidation, no shared tier — fails §23/§25.

### Approach C: True per-file incremental extraction

**Description:** Refactor FastAPI/Spring/Go extractors to per-file units with merge.
**Pros:** real parse savings. **Cons:** cross-file route/model resolution breaks; large regression risk across 3 extractors for a cache that already hits on unchanged trees. Deferred.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28 — pre-approved autonomous delivery of the remaining program |
| **Reasoning** | Meets §21–25/§48–51 with existing primitives; honest incremental claim |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Cache is advisory; recompute always correct | Cache miss/corruption → recompute, never an error | Failing on corrupt cache |
| 2 | Stale-critical never reused; stale-harmless reuse emits warning in receipt | §25 | Silent reuse |
| 3 | Graph key = sha of case inputs (case/api-ir/facts/findings) | Fixes case_id-only staleness | Keep case_id key |
| 4 | Delta via read-only git argv; `--changed` for hostless | No mutation, no shell | libgit/SDK |
| 5 | Shared tier opt-in, content-verified | Locality-first, no foreign trust | Always-global cache |
| 6 | L8 model-response declared disabled | No model answers in core; no fake savings | Implementing speculative response cache |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Per-file incremental re-extraction | Cross-file resolution; cache already hits unchanged trees | Yes |
| L8 model-response cache | No model responses in offline core | Yes (Wave 4/5 host path) |
| Remote/distributed cache | Local-first; no network | Yes |
| Background daemon/watcher | Not needed for CLI/MCP flow | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Layer scope + freshness model | ✅ | Autonomous mandate; aligned with §24–25 | No |
| Delta + invalidation flow | ✅ | Autonomous mandate; aligned with §21–23 | Yes — hostless `--changed` added |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
Every API Forge context request recomputes graph and capsule from scratch and the graph cache can serve stale evidence, so repeated or PR-scoped work pays full cost with no freshness guarantee.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Agent host (Claude/Codex/Devin) | Re-pays capsule/graph cost per turn; no PR delta entry point |
| Maintainer / CI | Cannot tell what was reused or why; stale evidence risk |

### Success Criteria (Draft)
- [ ] Unchanged rebuild of every corpus capsule is a cache hit and byte-identical.
- [ ] Mutating a model invalidates only capsules whose deps include it; unrelated capsules stay hits.
- [ ] `stale_reuse == 0` across the corpus; stale-critical always recomputed.
- [ ] `context delta --base --head` lists changed nodes, impacted operations and capsule targets.
- [ ] Shared tier reuses across two roots with identical inputs; corrupted object → recompute.

### Constraints Identified
- No provider SDK, no network, no shell; git read-only argv.
- Every refusal keeps `AF-*` code + `field` + `unlock`, cataloged.
- Default behavior preserved: cache on, repo-local; outputs byte-identical to uncached.

### Out of Scope (Confirmed)
- Per-file re-extraction, L8 responses, remote cache, daemon.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 4 |
| Validations Completed | 2 |
| Duration | ~15 min |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md`
