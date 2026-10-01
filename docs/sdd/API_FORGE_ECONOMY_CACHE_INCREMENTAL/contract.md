---
sdd: 1
feature: API_FORGE_ECONOMY_CACHE_INCREMENTAL
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "c13b73d8fea6b2c3a55c3a80d7ab2464abf12c7e7ce6e54e1053eceb792bced9"
covers:
- CacheDep/v1
- CacheEntry/v1
- CacheDecision/v1
- DeltaSlice/v1
api_ir:
  input: capsule request, case graph, project sources, git refs or changed paths
  output: cache decisions, cached selections, delta slices
---
# contract

No existing contract changes shape. `ContextCapsule/v1` output is byte-identical with and without the cache; cache metadata lives only in the store and the ledger `cache_hits`.
