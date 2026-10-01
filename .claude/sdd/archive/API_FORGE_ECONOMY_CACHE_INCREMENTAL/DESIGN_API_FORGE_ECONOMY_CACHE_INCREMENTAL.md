# DESIGN: API Forge Economy — Cache & Incremental Intelligence (Onda 2)

> Freshness-aware layered cache with dependency-aware invalidation and a delta-first entry point, built on the existing CAS, graph node hashes and impact traversal.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_CACHE_INCREMENTAL |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md](./DEFINE_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
context capsule --target T                     context delta --base A --head B | --changed f..
        │                                                   │
        ▼                                                   ▼
 load_case ──► L2 graph cache (.apiforge/ctx/graph/<inputs16>)   git diff --name-status (argv, RO)
        │                                                   │ changed files
        ▼                                                   ▼
 L4 selection lookup ──(CacheStore)──► CacheDecision     map files → fact nodes → operations
   key = sha(target, impact, SELECTION_VERSION)             + contract diff (openapi diff_contracts)
   freshness:                                               + entries whose deps hold the file
     dep files sha   ─┐                                     │
     graph neighborhood sha ─┼─► fresh|stale|invalidated   ▼
     symbol scan of changed ─┘                         DeltaSlice/v1 (targets, unresolved)
        │ hit → cached Selection      miss → select() ──► L3 impact memo per (graph, fact, mode)
        ▼                                                   │ --invalidate
 envelope recomposed (fingerprint, budget) → identical bytes ▼
        ▼                                             CacheStore.invalidate(files, nodes)
 ledger: cache_hits attributed

CacheStore tiers: local <root>/.apiforge/cache/{entries/<layer>/<key>.json, objects via ctx CAS}
                  shared (opt-in) $APIFORGE_CACHE_HOME/{entries,objects} — re-hashed on read
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `contracts/cache.py` | `CacheEntry/v1`, `CacheDep/v1`, `CacheDecision/v1`, `DeltaSlice/v1` | pydantic `VersionedContract` |
| `rules/cache_policies.yaml` | Per-layer policy: `enabled`, `ttl_seconds`, `on_stale` (`warn`/`recompute`), `shared` | YAML |
| `cache/policy.py` | Load + validate policy table | PyYAML |
| `cache/store.py` | `CacheStore`: lookup/put/invalidate/stats/gc across local + shared tiers | stdlib json, ctx CAS |
| `cache/freshness.py` | `assess(entry, policy, now, probe)` → `CacheDecision` | pure |
| `context/gateway/selection_cache.py` | Serialize/restore `Selection`, compute deps (files, nodes, neighborhood, symbols) | pure |
| `context/gateway/levels.py` | L2 graph key by inputs digest; L3 impact memo | existing |
| `context/gateway/capsule.py` | L4 lookup/store around `select()`; ledger `cache_hits` | existing |
| `context/delta.py` | `build_delta()` → `DeltaSlice/v1`; read-only git | subprocess argv |
| `cli_cache.py` + `cli_context.py` | `cache stats|invalidate`, `context delta|gc`, `--no-cache` | typer |
| `mcp/tools.py` | `cache_stats`, `cache_invalidate`, `context_delta`, `context_gc` | parity |
| `evals/cache.py` + corpus | Warm/mutate/rebuild scenarios with gates | fixture-based |

---

## Key Decisions

### Decision 1: Cache the evidence *selection*, recompose the capsule envelope

**Context:** The capsule embeds `fingerprint.case_id`, which changes whenever any analyzed input changes. Caching the whole capsule would force all-miss on any edit, or return stale bytes.
**Choice:** L4 caches the `Selection` (impact, candidates, policies, unresolved minus fingerprint). The envelope (fingerprint, budget admission, ids) is recomposed from the current case every call.
**Rationale:** Selection is the expensive part (graph impact, contract schema resolution, model scan, handler slicing); recomposition keeps output byte-identical to an uncached build.
**Alternatives Rejected:** whole-capsule cache (stale fingerprint); key on case_id (no precision).
**Consequences:** Hit still loads the case and graph (L2 cached).

### Decision 2: Freshness by dependency probes, not only TTL

**Choice:** Entry records `deps` = files (root-relative path + sha256), graph node ids, `neighborhood_sha` (sorted edges touching those nodes + their node sha), `symbols` (schema names, handler names, target path) and `manifest_uri` (CAS object of the project source manifest at build time). Lookup:
1. any dep file sha differs / missing → `invalidated` (changed source);
2. neighborhood sha differs in current graph → `invalidated`;
3. files changed vs manifest whose text contains a recorded symbol → `invalidated` (a new model/route could enter the selection);
4. past `expires_at` → `stale`; policy `on_stale: recompute` → `stale_critical` (recompute), `warn` → `stale_harmless` (reuse + warning);
5. else `fresh`.
**Rationale:** §23 precision without trusting TTL; conservative symbol scan protects recall.
**Alternatives Rejected:** full source digest in key (any edit → all miss).

### Decision 3: Advisory cache

Every read failure (missing object, hash mismatch, invalid JSON/contract) is `corrupt` → recompute. The cache never raises on read; only disabled layers and invalid CLI inputs refuse.

### Decision 4: Shared tier opt-in and content-verified

`APIFORGE_CACHE_HOME` or `--cache-home` enables the shared tier. Keys are root-independent (dep paths are root-relative), so identical inputs in another root hit. Objects are re-hashed on read; local tier is consulted first; shared hits are copied into the local ctx store after verification.

### Decision 5: Delta is read-only git or explicit list

`git -C <root> diff --name-status <base> [<head>]` via argv; failure → `AF-DELTA-GIT-UNAVAILABLE` / `AF-DELTA-REF-INVALID`. `--changed` works without git. Contract changes use `openapi.diff_contracts` on `git show <base>:<path>` vs head/worktree; without base content every operation of that contract is impacted (conservative) and `contract-diff-unavailable` is recorded.

### Decision 6: L2 graph keyed by case-file digest

`.apiforge/ctx/graph/<sha(case.json|api-ir|facts|findings)[:16]>` replaces the case_id key.

### Decision 7: Layers declared honestly

L1 parse = existing extractor cache (whole project, unchanged); L2/L3/L4 enforced; L5–L7 declared (`enabled: false` until a caller exists); L8 model-response `enabled: false` → `AF-CACHE-LAYER-DISABLED`.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/cache.py` | Create | Contracts | @python-developer | — |
| 2 | `src/apiforge/contracts/{__init__,registry}.py` | Modify | Register 4 contracts | @python-developer | 1 |
| 3 | `src/apiforge/rules/cache_policies.yaml` | Create | Layer policy | @python-developer | — |
| 4 | `src/apiforge/cache/{__init__,policy,freshness,store}.py` | Create | Store + freshness | @python-developer | 1,3 |
| 5 | `src/apiforge/context/gateway/selection_cache.py` | Create | Selection (de)serialization + deps | @python-developer | 4 |
| 6 | `src/apiforge/context/gateway/{levels,capsule}.py` | Modify | L2 key, L3 memo, L4 lookup | @python-developer | 5 |
| 7 | `src/apiforge/context/delta.py` | Create | DeltaSlice | @python-developer | 4,6 |
| 8 | `src/apiforge/cli_cache.py`, `cli_context.py`, `cli.py`, `application/context.py` | Create/Modify | CLI | @python-developer | 4,7 |
| 9 | `src/apiforge/mcp/tools.py` | Modify | MCP parity | @python-developer | 8 |
| 10 | `src/apiforge/evals/cache.py`, `evals/corpus/economy-cache/*` | Create | Eval + gates | @test-generator | 6,7 |
| 11 | `tests/cache/*`, `tests/context/test_delta.py`, `tests/mcp/test_cache_tools.py` | Create | Tests | @test-generator | all |
| 12 | `docs/contracts/{CacheEntry,CacheDep,CacheDecision,DeltaSlice}-v1.md`, `docs/catalog-contract.md`, `scripts/check_release.py`, `README.md` | Create/Modify | Docs + AF parity | @code-documenter | all |
| 13 | `docs/sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/*` | Create | SDD chain + evidence | (general) | all |

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1–9 | Typed pure-Python modules, pydantic |
| @test-generator | 10–11 | pytest fixtures + eval corpus |
| @code-documenter | 12 | Contract docs + catalog |

Executed inline by the build agent (small, coupled surface).

---

## Code Patterns

### Pattern 1: Advisory lookup

```python
decision, payload = store.lookup("capsule", key, probe=probe)
if decision.action in {"reuse", "reuse_warn"} and payload is not None:
    selection = restore(payload)
else:
    selection = select(...)
    store.put(entry_for(selection, key, deps), dumps_text(selection))
```

### Pattern 2: Refusal

```python
raise GatewayError("AF-DELTA-GIT-UNAVAILABLE", f"{root} is not a git work tree",
                   field="root", unlock="pass --changed <file> ... instead of --base/--head")
```

### Pattern 3: Policy file

```yaml
schema: apiforge/cache-policies/v1
layers:
  capsule: {enabled: true, ttl_seconds: 604800, on_stale: recompute, shared: true}
  model_response: {enabled: false, ttl_seconds: 0, on_stale: recompute, shared: false}
```

---

## Data Flow

1. `build_capsule` loads case → graph (L2 by content key).
2. Compute L4 key; `store.lookup` evaluates freshness probes against current files + graph.
3. Hit: restore Selection; ensure ctx objects (copy from shared if needed). Miss: `select()` (L3 impact memo inside), store entry.
4. `_admit` + `_finish` unchanged → identical bytes; ledger envelope row carries `cache_hits`.
5. `context delta` maps changed files to impacted operations; `--invalidate` drops affected entries.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| git CLI | read-only argv subprocess (`diff --name-status`, `show`) | none |
| ctx CAS | `CtxStore` put/get with hash verification | none |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | freshness states, policy load, store tiers, corrupt reads, gc | `tests/cache/` | pytest | all branches of `assess` |
| Integration | capsule hit identical bytes, precise invalidation, graph key | `tests/context/test_capsule_cache.py` | pytest + fixture | AT-001..004 |
| Integration | delta git + explicit + refusals | `tests/context/test_delta.py` | pytest + tmp git repo | AT-006/007 |
| Parity | CLI == MCP | `tests/mcp/test_cache_tools.py` | CliRunner | 4 tools |
| Eval | corpus gates | `evals cache` | CLI | stale_reuse 0, precision/recall 1.0 |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Corrupt entry/object | decision `corrupt` → recompute + overwrite | No |
| Disabled layer | `AF-CACHE-LAYER-DISABLED` (field `layer`) | No |
| Unknown layer | `AF-CACHE-LAYER-UNKNOWN` | No |
| Invalid policy file | `AF-CACHE-POLICY-INVALID` | No |
| No git / bad ref | `AF-DELTA-GIT-UNAVAILABLE` / `AF-DELTA-REF-INVALID` | No |
| No delta input | `AF-DELTA-INPUT-MISSING` | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `APIFORGE_CACHE` | env | `on` | `off` disables L3/L4 lookups (outputs identical) |
| `APIFORGE_CACHE_HOME` | env | unset | enables shared tier |
| `--no-cache` / `--cache-home` | CLI | — | per-call overrides |
| `rules/cache_policies.yaml` | YAML | shipped | ttl/on_stale per layer |

---

## Security Considerations

- No shell; git argv only; read-only commands.
- Shared tier never trusts bytes: sha256 verified on every read.
- Entries hold root-relative paths only (no absolute paths leak across roots).
- `context gc` deletes only with `--apply`, only under cache/ctx dirs.

---

## Observability

- `CacheDecision` returned in `cache stats` and in capsule ledger rows (`cache_hits`).
- `context delta` output lists `unresolved` (unmapped files, contract diff unavailable).

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md`
