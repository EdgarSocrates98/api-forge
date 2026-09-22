---
sdd: 1
feature: API_FORGE_AGENTIC_RUNTIME_PHASE_A
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "f09b08e9663d03f202c4e7dcfd608549541cb9b826d30e56697f6dcd9eb2da2c"
covers: [RuntimeReview/v1, AgentInvocation/v1]
api_ir:
  input: sealed TaskSpec and invocation plan
  output: review digest, bounded invocations and checkpoint events
---
# contract

Reviews vinculam revisão à revisão do TaskSpec; scheduler e checkpoints preservam orçamento e proveniência.
