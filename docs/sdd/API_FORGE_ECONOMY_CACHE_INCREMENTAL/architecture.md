---
sdd: 1
feature: API_FORGE_ECONOMY_CACHE_INCREMENTAL
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "6792d38462e119098c9396cd8b3d8013eaffd210995fb19bd0a8d976f7fa77cb"
files:
- src/apiforge/contracts/cache.py
- src/apiforge/rules/cache_policies.yaml
- src/apiforge/cache/policy.py
- src/apiforge/cache/freshness.py
- src/apiforge/cache/store.py
- src/apiforge/cache/errors.py
- src/apiforge/context/gateway/selection_cache.py
- src/apiforge/context/gateway/levels.py
- src/apiforge/context/gateway/capsule.py
- src/apiforge/context/delta.py
- src/apiforge/application/cache.py
- src/apiforge/cli_cache.py
- src/apiforge/evals/cache.py
decisions:
- id: selection-not-envelope
  decision: L4 caches the evidence selection; fingerprint and budget admission are recomposed each call
  rollback: pass --no-cache or APIFORGE_CACHE=off
- id: probe-freshness
  decision: dependency probes (file/span/pointer hashes, graph neighborhood, model definitions, test mentions)
    run before TTL
  rollback: delete .apiforge/cache
- id: advisory-cache
  decision: any unreadable entry or tampered object is a corrupt miss that recomputes
  rollback: none needed
- id: graph-content-key
  decision: L2 graph snapshots are keyed by the digest of the case artifacts
  rollback: restore case_id keying
- id: read-only-delta
  decision: delta uses git argv diff/show only, or an explicit --changed list
  rollback: remove context delta
- id: opt-in-shared-tier
  decision: shared tier only with APIFORGE_CACHE_HOME or --cache-home, re-hashed on read
  rollback: unset the env
---
# architecture

contracts → cache (policy, freshness, store) → gateway selection cache → capsule; delta depends on the store and the graph. The cache package imports nothing from the gateway to avoid an import cycle.
