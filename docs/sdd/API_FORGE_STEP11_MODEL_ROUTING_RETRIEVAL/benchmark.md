---
sdd: 1
feature: API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1596 passed, 2 skipped (phase-5 wave baseline)
  recorded_at: "2026-10-06"
results:
  - "focused suite: 69 passed in 76s (model router + levels + knowledge + evals)"
  - "evals model-routing: 3/3 deterministic, no provider calls"
  - "evals retrieval: 1/1 case; strategy latencies measured per run"
  - "routing is O(candidates) constraint checks then O(candidates) scoring; the ladder is O(levels x search) and stops at first sufficient level"
upstream:
  path: secure.md
  sha256: "aa3d504eb3b51cbdcd44ad97373163a2ecf729528e87ef126408249693df011d"
---

# benchmark

No hot path: routing and retrieval run on demand from the CLI/MCP surface.
The economy win is L1 stopping early — most queries never climb past
lexical search, and L4 rerank cost is paid only when every cheaper level
failed.
