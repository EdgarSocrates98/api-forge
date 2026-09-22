---
sdd: 1
feature: API_FORGE_AGENTIC_RUNTIME_PHASE_A
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "06361aad2e79375e37b9a8232875813fc0e32f6a5f1820ef67e280ade50f60c7"
files: [src/apiforge/runtime/review.py, src/apiforge/runtime/scheduler.py, src/apiforge/runtime/supervisor.py, src/apiforge/contracts/agentic.py]
decisions:
  - id: digest-review
    decision: persistir RuntimeReview antes de iniciar workers
    rationale: detectar drift e bloquear TaskSpec inválido
    rollback: manter review legado sem digest
  - id: batch-parallelism
    decision: calcular limite por batch dentro do limite da policy
    rationale: permitir paralelismo dinâmico sem ultrapassar orçamento
    rollback: usar max_parallel_agents fixo
---
# architecture

O supervisor continua determinístico; o scheduler recebe função de paralelismo e o store registra checkpoints por invocação.
