---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1685 passed, 2 skipped (phase-11 wave baseline)
  recorded_at: "2026-10-08"
results:
  - "focused suite: 26 passed in ~6s (knowledge evolution, lab, doctor, freshness, MCP surface)"
  - "evals knowledge-drift: 5/5 deterministic, O(receipts^2) conflict pairing"
  - "knowledge impact: builds 342-node/454-edge graph over 40 packs in <1s, declared-data only"
  - "lab scenarios: catalog parse + validation O(cells), instant"
  - "doctor --agentic: 8 plane probes over persisted files, sub-second"
  - "supply_chain_audit: inventory + vendor parity + corpus walk, <2s offline"
  - "token cost: zero — the entire phase is deterministic and offline"
upstream:
  path: secure.md
  sha256: "16127889c8cd3c47c3fa5bd9521b7448bb4c57c8bdc6b1f485ae4801258cb9e6"
---

# benchmark

All new surfaces are deterministic file/graph walks bounded by declared
inputs. No model calls, no provider spend, no network wait. The full
suite (1685 passed baseline + 26 new focused tests merged into it)
runs in the final wave.
