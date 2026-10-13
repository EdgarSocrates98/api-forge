---
sdd: 1
feature: API_FORGE_PERFORMANCE_CAPACITY_VALIDATION_C
phase: discover
profile: standard
status: draft
approaches:
  - id: raw-tps-claim
    summary: tratar o maior TPS observado como capacidade segura
    verdict: refused -- ignora SLO, evidência e headroom
  - id: evidence-bound-envelope
    summary: derivar envelope somente de run aprovado e política declarada
    verdict: chosen -- reproduzível e seguro
chosen: evidence-bound-envelope
---
# discover

O veredito existente valida uma execução, mas ainda faltava um artefato explícito de capacidade para planejamento e CI.
