---
sdd: 1
feature: API_FORGE_ECONOMY_SELECTIVE_AGENTICS
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "b22aa36ab093ec15dcb6b74e202b5272b71a6f924677e96e1c597077d61afe6f"
tasks:
- id: contracts
  status: done
  evidence: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
- id: selector
  status: done
  evidence: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
- id: role-context
  status: done
  evidence: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
- id: debate
  status: done
  evidence: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
- id: shadow
  status: done
  evidence: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
- id: audit
  status: done
  evidence: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
- id: eval
  status: done
  evidence: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-eval.json
claims:
- lazy-expertise
- role-context
- position-deltas
- referee-packet
- bounded-shadow
- agent-audit
- selective-eval
---
# build

Implemented `knowledge select`, `debate submit --disagree/--risk/--confidence`, `debate packet`, `agents audit`, role context in `runtime run`, the shadow block and `apiforge evals selective-agentics`, with MCP parity.
