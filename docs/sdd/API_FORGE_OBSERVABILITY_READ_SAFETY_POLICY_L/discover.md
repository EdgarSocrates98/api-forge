---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_SAFETY_POLICY_L
phase: discover
profile: standard
status: draft
approaches:
  - id: unbounded-response
    summary: aceitar qualquer resposta do provider
    verdict: refused -- risco de memória, cardinalidade e custo
  - id: deterministic-budgets
    summary: limitar registros e bytes antes de expor dados ao core
    verdict: chosen -- comportamento previsível e testável
chosen: deterministic-budgets
---
# discover

A leitura autenticada precisava de uma barreira contra respostas excessivas antes da normalização no runtime.
