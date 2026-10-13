---
sdd: 1
feature: API_FORGE_AGENTIC_RUNTIME_PHASE_A
phase: discover
profile: standard
status: draft
approaches:
  - id: executor-only
    summary: executar TaskSpec sem revisão independente e sem checkpoint
    verdict: refused -- reduz auditabilidade e retomada
  - id: reviewed-dynamic-runtime
    summary: review digest-bound, scheduler bounded e checkpoints
    verdict: chosen -- base verificável para autonomia
chosen: reviewed-dynamic-runtime
---
# discover

O runtime já executava invocações, mas precisava provar a revisão, controlar chamadas e registrar progresso incremental.
