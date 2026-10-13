---
sdd: 1
feature: API_FORGE_ECONOMY_CACHE_INCREMENTAL
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "e3f5b19111c38c657df257f0c1ebfea0a41632c00d7a87391c80637fbda86c10"
tasks:
- id: contracts
  status: done
  evidence: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
- id: store
  status: done
  evidence: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
- id: selection-cache
  status: done
  evidence: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
- id: delta
  status: done
  evidence: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
- id: eval
  status: done
  evidence: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-eval.json
claims:
- layered-cache-policy
- freshness-decisions
- selection-cache-identical-bytes
- dependency-invalidation
- delta-first
- shared-tier
- cache-eval
---
# build

Implemented `cache stats|invalidate`, `context delta|gc`, `--no-cache`/`--cache-home` on `context capsule`, matching MCP tools and `apiforge evals cache`.
