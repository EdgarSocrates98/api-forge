---
sdd: 1
feature: API_FORGE_ECONOMY_CACHE_INCREMENTAL
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "3df9530ce95148e6674bd73fb7e25d3d518329d89b9b2e6094c91c274bdd3067"
tasks:
- id: contracts
  covers:
  - CacheDep/v1
  - CacheEntry/v1
  - CacheDecision/v1
  - DeltaSlice/v1
  test: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
  risk: low
  rollback: remove contracts/cache.py and registry rows
- id: store
  covers:
  - layered-cache-policy
  - freshness-decisions
  - shared-tier
  test: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
  risk: low
  rollback: remove src/apiforge/cache
- id: selection-cache
  covers:
  - selection-cache-identical-bytes
  - dependency-invalidation
  test: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
  risk: medium
  rollback: APIFORGE_CACHE=off
- id: delta
  covers:
  - delta-first
  test: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
  risk: low
  rollback: remove context/delta.py
- id: eval
  covers:
  - cache-eval
  test: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-eval.json
  risk: low
  rollback: remove evals/cache.py and the corpus
---
# plan

Contracts, store and policy, gateway integration, delta, surfaces, eval. Targeted tests per task; full suite once before push.
