---
sdd: 1
feature: API_FORGE_ECONOMY_CACHE_INCREMENTAL
phase: discover
profile: standard
status: draft
approaches:
- id: unified-cache-entry
  summary: one CacheEntry/v1 store with per-layer policy, dependency probes and a delta verb
  verdict: chosen -- reuses ctx CAS, graph node hashes and impact traversal
- id: ad-hoc-layer-caches
  summary: patch the graph key and memoize capsules on disk
  verdict: refused -- no freshness model or dependency invalidation
- id: per-file-extraction
  summary: refactor extractors to per-file incremental units
  verdict: refused -- cross-file resolution risk for a cache that already hits on unchanged trees
chosen: unified-cache-entry
---
# discover

Source: `prompt_evo_economy.md` §21–§25 and §48–§51. The gateway graph cache was keyed by `case_id`; capsules were rebuilt from scratch every call; there was no delta entry point.
