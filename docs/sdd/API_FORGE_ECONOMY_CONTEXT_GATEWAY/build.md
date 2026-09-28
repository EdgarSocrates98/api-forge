---
sdd: 1
feature: API_FORGE_ECONOMY_CONTEXT_GATEWAY
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "4e2acd9a40ee17cbd6ed0c47618bbff8166a4bda2fa3913ce2ab628f7b1d1164"
tasks:
  - id: contracts
    status: done
    evidence: sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/evidence/economy-tests.txt
  - id: gateway
    status: done
    evidence: sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/evidence/economy-tests.txt
  - id: attribution
    status: done
    evidence: sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/evidence/economy-tests.txt
  - id: eval-gate
    status: done
    evidence: sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/evidence/economy-eval.json
claims: [capsule-ctx-refs, hash-verified-expand, attributed-ledger, economy-eval-gate]
---
# build

Implemented `apiforge context capsule|expand`, `apiforge economy stats|explain`,
`apiforge evals economy` and the matching MCP tools, plus the
`economy_payments` fixture and a 12-case corpus.
