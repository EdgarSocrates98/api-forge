---
sdd: 1
feature: API_FORGE_AGENTIC_QUALITY_HOST_PARITY_G
phase: discover
profile: standard
status: draft
approaches:
  - id: average-quality
    summary: reduzir todos os evals a uma média
    verdict: refused -- oculta holdout e casos bloqueados
  - id: evidence-aggregate
    summary: agregar golden, holdout e paridade preservando lacunas
    verdict: chosen -- decisão auditável por host
chosen: evidence-aggregate
---
# discover

Golden e holdout já existem, assim como auditoria de host; faltava uma visão agregada sem mascarar gaps.
