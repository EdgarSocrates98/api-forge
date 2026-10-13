---
sdd: 1
feature: API_FORGE_ECONOMY_CONTEXT_GATEWAY
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "677978fa8035f39733f6fddb66ffe42f007759e5cc55da5418bbba2ea0cca703"
tasks:
  - id: contracts
    covers: [ContextRef/v1, ContextCapsule/v1, CostVector/v1, RunLedgerEntry/v1, capsule-ctx-refs]
    test: sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/evidence/economy-tests.txt
    risk: low
    rollback: remove the new contracts from the registry
  - id: gateway
    covers: [capsule-ctx-refs, hash-verified-expand, canonical-serialization, schema-dedup]
    test: sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/evidence/economy-tests.txt
    risk: medium
    rollback: remove context/gateway and the context capsule|expand commands
  - id: attribution
    covers: [attributed-ledger, economy-stats, economy-explain]
    test: sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/evidence/economy-tests.txt
    risk: low
    rollback: remove run_ledger.py and cli_economy.py
  - id: eval-gate
    covers: [economy-eval-gate, catalog-codes]
    test: sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/evidence/economy-eval.json
    risk: low
    rollback: remove evals/economy.py and evals/corpus/economy
---
# plan

Contracts first, then store and selection, then ledger attribution, then the
benchmark corpus and surfaces. Targeted tests per task; full suite once.
