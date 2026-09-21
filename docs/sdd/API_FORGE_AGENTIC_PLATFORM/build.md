---
sdd: 1
feature: API_FORGE_AGENTIC_PLATFORM
phase: build
profile: critical
status: draft
upstream:
  path: plan.md
  sha256: "e4316a4be25d51dfb9a2fcde949692115be1786c200eeff96e8e03adac79bcbe"
tasks:
  - id: A1
    outcome: done
    evidence: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/A1.txt
  - id: A2
    outcome: done
    evidence: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/A2.txt
  - id: B1
    outcome: done
    evidence: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/B1.txt
  - id: B2
    outcome: done
    evidence: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/B2.txt
  - id: B3
    outcome: done
    evidence: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/B3.txt
claims:
  - "contract list/show emits JSON schema for every registered v1 contract; unknown names refuse AF-CONTRACTS-UNKNOWN"
  - "task seal binds an Ed25519 signature to the exact revision; amending a sealed task writes a new unsealed revision"
  - "task run executes recipes through dispatch_step inside budgets with a no-progress breaker"
  - "task accept refuses accepted_by == executed_by"
  - "brief show refuses DONE while gaps, missing acceptance, or open items remain"
---

# build

Spec A delivered `apiforge/contracts/` (registry + versioned models +
conformance tests). Spec B delivered `apiforge/taskspec/` (store, closed
state machine, Ed25519 seal, budgets + no-progress breaker, acceptance) and
`apiforge/brief/` (OutcomeBrief with DONE-refusal). The task runner reuses
`dispatch_step` -- the same unit `dispatch run` executes -- and a `case=`
task input binds `evidence emit` to a real case directory.
