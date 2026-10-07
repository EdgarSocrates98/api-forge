# DEFINE: API Forge Economy — Cache & Incremental Intelligence (Onda 2)

> Freshness-aware multi-level cache, dependency-aware invalidation and delta-first context so repeated and PR-scoped work reuses verified evidence instead of recomputing it.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_CACHE_INCREMENTAL |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md` |

---

## Problem Statement

Every `context capsule` rebuilds the case graph and the capsule from scratch, and the gateway graph cache is keyed by `case_id` alone, so a re-analyzed case can serve stale graph evidence. There is no freshness model, no dependency-aware invalidation, no delta (base/head) entry point and no cross-repository reuse, so PR-scoped and repeated agent work pays full cost with no guarantee the reused evidence is current.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Agent host (Claude/Codex/Devin) | Calls `context capsule`/MCP each turn | Pays graph + capsule cost on every call; no "what changed" entry |
| Maintainer / CI | Reviews PRs via change-control and capsules | Cannot see what was reused, why, or whether it was fresh |
| Workspace owner | Multi-repo API workspace | Identical inputs across repos recomputed per repo |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | G1: `CacheEntry/v1` + `CacheDecision/v1` contracts: layer, key, `inputs_sha`, `source_sha`, `policy_sha`, `expertise_sha`, `deps`, `created_at`, `expires_at`, freshness state; registered and documented |
| **MUST** | G2: Layer policy table `rules/cache_policies.yaml` for L1 parse, L2 graph, L3 impact, L4 capsule (enforced), L5 knowledge, L6 routing, L7 validation (declared), L8 model-response (declared `disabled`) |
| **MUST** | G3: Freshness decision (§25): `fresh→reuse`, `stale_harmless→reuse+warning`, `stale_critical→recompute`, `changed source→invalidate`; stale-critical never reused |
| **MUST** | G4: Graph cache keyed by digest of case inputs (fixes case_id-only staleness) |
| **MUST** | G5: Capsule cache (L4): key = target + budget + level + impact + action/objective + graph digest + policy digest; hit returns byte-identical capsule and is attributed in the ledger (`cache_hits`) |
| **MUST** | G6: Dependency-aware invalidation (§23): changed files → changed graph nodes (node sha diff + fact source file) → reverse-edge dependents → only entries whose `deps` intersect are invalidated |
| **MUST** | G7: Delta-first (§22): `DeltaSlice/v1` from read-only `git diff --name-status base..head` or explicit `--changed`; lists changed files, changed nodes, impacted operations, suggested capsule targets, unresolved |
| **SHOULD** | G8: Shared CAS tier (§50–51): opt-in `APIFORGE_CACHE_HOME`/`--cache-home`; objects re-hashed on read; corrupt → recompute |
| **SHOULD** | G9: `cache stats`, `cache invalidate`, `context gc` (report by default, `--apply` deletes) CLI + MCP parity |
| **SHOULD** | G10: `evals cache` corpus + gates (hit rate, invalidation precision/recall, stale reuse 0) |
| **COULD** | G11: Extractor cache (L1) emits `CacheEntry` metadata so all layers report uniformly |

---

## Success Criteria

- [ ] 100% of corpus capsules rebuilt on unchanged inputs are L4 hits and byte-identical to the uncached build.
- [ ] Model mutation invalidates exactly the capsules whose deps contain it: invalidation precision = 1.0 and recall = 1.0 on the corpus.
- [ ] `stale_reuse == 0` across corpus (no stale-critical entry ever reused).
- [ ] `context delta` on a 1-file change returns ≥ 1 impacted operation and its capsule target, with 0 git mutations.
- [ ] Shared tier: second root with identical inputs gets ≥ 1 hit; a tampered object is recomputed, not trusted.
- [ ] Existing gateway/economy tests unchanged-green (capsule bytes unchanged when cache disabled).

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Warm hit | analyzed fixture, capsule built | build same capsule again | `cache: hit`, identical bytes, ledger `cache_hits ≥ 1` |
| AT-002 | Graph freshness | graph cached; facts.json changed, same case_id | build capsule | graph recomputed (new inputs digest), no stale graph |
| AT-003 | Precise invalidation | capsules for 2 ops warm; model used by op A changed | `cache invalidate --changed <model file>` | op A entries invalidated, op B entries kept |
| AT-004 | Stale critical | L4 entry past `expires_at`, policy `on_stale: recompute` | build capsule | recompute, decision `stale_critical` |
| AT-005 | Stale harmless | L7 entry expired, policy `on_stale: warn` | lookup | reuse with warning in decision |
| AT-006 | Delta git | repo with 2 commits changing a model | `context delta --base A --head B` | changed nodes + impacted ops + targets |
| AT-007 | Delta no git | non-git root | `context delta --base A --head B` | `AF-DELTA-GIT-UNAVAILABLE` with field/unlock; `--changed` works |
| AT-008 | Corrupt entry | entry file invalid JSON / object hash mismatch | lookup | miss + recompute, never error |
| AT-009 | Shared tier | two roots, same inputs, same cache home | build in root 2 | hit from shared tier |
| AT-010 | gc | orphan ctx objects + expired entries | `context gc` / `--apply` | report lists them / deletes them only with `--apply` |
| AT-011 | L8 disabled | lookup layer L8 | any | `AF-CACHE-LAYER-DISABLED` |

---

## Out of Scope

- Per-file incremental re-extraction (extractors stay whole-project; reuse via L1).
- Model-response cache implementation (L8 declared disabled).
- Remote/distributed cache, background daemon/file watcher.
- Git mutation of any kind.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | No provider SDK, no network, argv-only git, no `shell=True` | `git diff --name-status` via subprocess, read-only |
| Technical | Cache advisory: any cache failure → recompute | Store never raises on read corruption |
| Technical | Every refusal keeps `AF-*` + `field` + `unlock`, cataloged in `docs/catalog-contract.md` | New codes documented |
| Technical | Default outputs byte-identical with and without cache | Capsule identity excludes cache metadata |
| Process | Targeted tests per task; full suite once before push | Per memory `full-suite-only-at-end` |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/cache/` (new), `contracts/cache.py`, `context/gateway/`, `context/delta.py`, `evals/cache.py`, `rules/cache_policies.yaml`, CLI/MCP | Extends gateway + graph store |
| **KB Domains** | pydantic, testing, python | Contract + deterministic tests |
| **IaC Impact** | None | Local-first |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Graph node sha covers props so node diff detects evidence changes | Missed invalidation | [x] `graph/store.py::node_sha256` |
| A-002 | Facts carry a source file path mappable to changed files | File→node mapping incomplete | [ ] verify in design |
| A-003 | Capsule output is deterministic for identical inputs | Hits not byte-identical | [x] economy eval `deterministic` gate |
| A-004 | `git` binary is optional; hostless path via `--changed` | Delta unusable offline | [x] design choice |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Concrete stale-graph bug + recompute cost |
| Users | 3 | Host, CI, workspace owner |
| Goals | 3 | MoSCoW with layer table |
| Success | 3 | Numeric gates |
| Scope | 2 | L5–L7 declared but only policy-level; boundary stated |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design. (A-002 verified during design.)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial version |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md`
