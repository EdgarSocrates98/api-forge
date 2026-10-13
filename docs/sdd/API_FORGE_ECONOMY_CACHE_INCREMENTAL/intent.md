---
sdd: 1
feature: API_FORGE_ECONOMY_CACHE_INCREMENTAL
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "d537723b38f396cc22812901aa10060a4bfa45aabcee497d1f14c3270b21019a"
problem: Every capsule rebuilds graph and selection from scratch, the graph cache is keyed by case id,
  and nothing maps a PR delta to the operations and evidence it touches.
success:
- layered-cache-policy
- freshness-decisions
- selection-cache-identical-bytes
- dependency-invalidation
- delta-first
- shared-tier
- cache-eval
out_of_scope:
- per-file-extraction
- model-response-cache
- remote-cache
- watcher-daemon
owner: api-forge-economy
risk_class: medium
risk_signals:
- path:src/apiforge/context/gateway/capsule.py
- path:src/apiforge/context/gateway/levels.py
- path:src/apiforge/cache/store.py
---
# intent

Reuse only evidence that is provably still true, invalidate only what a change touches, and start PR work from the delta.
