---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: contract
profile: critical
status: done
covers:
  - capability-matrix
  - task-lifecycle
  - risk-gate
  - governed-projection
  - evidence-bundle
  - peer-handoff
  - health-report
  - refusal-codes
  - cli-mcp-surface
  - eval-corpus
contracts:
  - ForgeCapabilityDescriptor/v1
  - ForgeTaskRequest/v1
  - ForgeTaskStatus/v1
  - ForgeTaskResult/v1
  - ForgeEvidenceArtifact/v1
  - ForgeEvidenceBundle/v1
  - ForgeHandoff/v1
  - ForgeHealth/v1
refusals:
  - AF-FORGE-POLICY
  - AF-FORGE-TASK-ID
  - AF-FORGE-TASK-EXISTS
  - AF-FORGE-TASK-NOT-FOUND
  - AF-FORGE-CAPABILITY-UNKNOWN
  - AF-FORGE-RISK-GATE
  - AF-FORGE-STATE
  - AF-FORGE-ENGINE-UNKNOWN
  - AF-FORGE-HANDOFF-EXISTS
  - AF-FORGE-HANDOFF-NOT-FOUND
  - AF-FORGE-STORE
upstream:
  path: intent.md
  sha256: "b33e9be9a14a7502245affedadce3d3963c6821db1415827642cd83a9ca5acc8"
---

# contract

Eight versioned contracts under `apiforge/forge-*/v1` schemas plus eleven
catalogued refusal codes. `ForgeTaskStatus.state` is a closed enum
(accepted/in_progress/completed/failed/refused); `ForgeTaskResult.status`
is `ok`/`review`/`unresolved` — never a fabricated DONE. `ForgeHandoff`
is `prepared` only; `delivered` is not a state the local boundary can
claim.
