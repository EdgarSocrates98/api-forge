---
sdd: 1
feature: API_FORGE_AGENTIC_RUNTIME_PHASE_A
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "037e470e6a77175948bb6d36be41c7e679d45196b8786270b37fa1a4db1ea22b"
tasks:
  - id: review
    covers: [runtime-review]
    test: sdd/API_FORGE_AGENTIC_RUNTIME_PHASE_A/evidence/runtime-tests.txt
    risk: high
    rollback: remover RuntimeReview
  - id: scheduler
    covers: [dynamic-parallelism]
    test: sdd/API_FORGE_AGENTIC_RUNTIME_PHASE_A/evidence/runtime-tests.txt
    risk: high
    rollback: restaurar scheduler fixo
  - id: checkpoints
    covers: [invocation-checkpoints]
    test: sdd/API_FORGE_AGENTIC_RUNTIME_PHASE_A/evidence/runtime-tests.txt
    risk: medium
    rollback: remover eventos checkpoint
---
# plan

Implementar review digest-bound, orçamento `max_calls`, paralelismo por batch e checkpoints.
