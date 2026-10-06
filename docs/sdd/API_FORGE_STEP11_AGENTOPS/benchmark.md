---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1621 passed, 2 skipped (phase-7 wave baseline)
  recorded_at: "2026-10-06"
results:
  - "focused suite: 18 passed, 1 skipped in ~3s"
  - "evals agentops: 4/4 deterministic, no provider calls"
  - "inspect is O(ledger rows + spans + memory jsonl); compare runs two
    inspections; waste adds the declared detector pass over the same rows"
upstream:
  path: secure.md
  sha256: "5aaa484170d0862f04b96aa68af713dbf6a33a45a2dec40a52d5351c3315d4c9"
---

# benchmark

Report generation is on-demand from CLI/MCP — nothing sits on a hot p
