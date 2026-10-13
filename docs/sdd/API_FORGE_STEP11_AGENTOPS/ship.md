---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: ship
profile: critical
status: done
deviations:
  - "provider cost stays unresolved — pricing lookup happens in economy cost, AgentOps reports the ledger truth"
  - "memory metrics are store-wide (rows carry no run_id); labeled estimated"
  - "text projection is the JSON itself; a rendered table is left for the TUI surface"
evidence:
  - docs/sdd/API_FORGE_STEP11_AGENTOPS/evidence/G1-focused-tests.txt
  - docs/sdd/API_FORGE_STEP11_AGENTOPS/evidence/G2-evals.txt
  - docs/sdd/API_FORGE_STEP11_AGENTOPS/evidence/G3-gates.txt
rollback: "revert this commit; all modules are additive — ledgers, spans and
  memory stores are untouched and older code never imports agentops.inspect"
upstream:
  path: benchmark.md
  sha256: "4dfc0dfaf068e6690f1409ed59be10185dc096e663085ddb53e7e9236496ce63"
---

# ship

Phase 8 delivered: the §54 sectioned run report, the §55 axis comparison
and the §56 declared-policy waste detector with §57 evidence labels — all
read-only over the local ledgers.
