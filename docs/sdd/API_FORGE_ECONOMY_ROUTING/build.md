---
sdd: 1
feature: API_FORGE_ECONOMY_ROUTING
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "ff734f2b082b7996978965c81428adfae7f3bd1eca1fb20f6209c43e055c8d02"
tasks:
  - id: contracts
    status: done
    evidence: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-tests.txt
  - id: economy-plane
    status: done
    evidence: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-tests.txt
  - id: risk-adaptive-sdd
    status: done
    evidence: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-tests.txt
  - id: eval
    status: done
    evidence: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-eval.json
claims: [economy-profiles, risk-floor-invariant, supervisor-envelope, stop-and-ladder, risk-adaptive-sdd]
---
# build

Implemented `--profile` on `runtime run|resume|debate` (CLI + MCP), the
economy block in runtime results, `sdd classify`, the `micro` SDD profile and
`apiforge evals economy-routing`.
