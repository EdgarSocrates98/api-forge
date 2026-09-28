---
sdd: 1
feature: API_FORGE_ECONOMY_SELECTIVE_AGENTICS
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "c68055577876491e0029049f2aee1be3c9bcb781a00a5a2be531f050104bef1e"
tasks:
- id: contracts
  covers:
  - ExpertiseSelection/v1
  - RoleContextPlan/v1
  - PositionDelta/v1
  - RefereePacket/v1
  - ShadowDecision/v1
  - AgentUniqueness/v1
  test: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
  risk: low
  rollback: remove contracts/selective.py and registry rows
- id: selector
  covers:
  - lazy-expertise
  test: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
  risk: low
  rollback: remove knowledge/selector.py
- id: role-context
  covers:
  - role-context
  test: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
  risk: medium
  rollback: economy_enabled=False
- id: debate
  covers:
  - position-deltas
  - referee-packet
  test: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
  risk: low
  rollback: remove debate/packet.py
- id: shadow
  covers:
  - bounded-shadow
  test: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
  risk: low
  rollback: 'shadow_share: 0'
- id: audit
  covers:
  - agent-audit
  test: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
  risk: low
  rollback: remove agentops/agent_audit.py
- id: eval
  covers:
  - selective-eval
  test: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-eval.json
  risk: low
  rollback: remove evals/selective.py and the corpus
---
# plan

Contracts and envelope fields, selector, planner, supervisor wiring, debate, shadow, audit, surfaces, eval.
