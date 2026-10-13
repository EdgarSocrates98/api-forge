---
sdd: 1
feature: API_FORGE_ECONOMY_SELECTIVE_AGENTICS
phase: ship
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "79c6eecafd316b9325da739a7696574126840e8ee62957917890a18a458c6048"
deviations:
- challengers-shadow-from-untrimmed-plan
- audit-flags-44-of-52-on-declared-data
- hosts-must-honor-context-refs
evidence:
- path: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-eval.json
  sha256: f388661418085ca37380d8ca37c2ff648dcafc0e1474b575fb349751cb5591c8
- path: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
  sha256: c7693b6ec6a2aaa0274fba63c91c4403abdb27137d37f8ef17c9201c194bbb39
---
# ship

Ready for review. Shadow candidates come from the routing plan before economy trims, so economy runs still sample challengers at 5%. The audit marks 44 of 52 agents as merge candidates because the catalog declares no runtime capability or unique rule area for them — a catalog-evidence gap, not an instruction to delete. Byte savings are realized only by hosts that honor `context_refs`.
