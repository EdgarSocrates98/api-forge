---
sdd: 1
feature: API_FORGE_ECONOMY_ROUTING
phase: ship
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "cf71a86ce0aff7a17b8ebbd3302fc7c1b48cd784e2efc4e734e59af938439d4f"
deviations: [default-balanced-changes-unprofiled-runs, live-baseline-instead-of-recorded, single-reviewer-catalog-limits-l3]
evidence:
  - path: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-tests.txt
    sha256: "d965848c7fa7e0bbbea99d40496ad3e66ae8a4c87dd916cf91f309ec5ebd3c26"
  - path: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-eval.json
    sha256: "27b2d5a7a234667a0038f331f5fcb346c6f661706247addd5262d0deadb1c9e4"
---
# ship

Ready for review. Runs without `--profile` now use the `balanced` envelope
(fewer optional specialists). The capability catalog has a single reviewer,
so an L3 escalation only occurs when risk does not already require it.
Waves 2, 4, 5 and 6 remain out of scope.
