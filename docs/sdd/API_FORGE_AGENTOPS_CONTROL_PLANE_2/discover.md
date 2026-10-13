---
sdd: 1
feature: API_FORGE_AGENTOPS_CONTROL_PLANE_2
phase: discover
profile: standard
status: done
approaches:
  - id: replace-runtime
    summary: substituir runtime AgenticRun existente
    verdict: refused -- quebra contratos já publicados
  - id: compose-control-plane
    summary: adicionar lifecycle persistente acima do runtime atual
    verdict: chosen -- preserva compatibilidade e permite evolução incremental
chosen: compose-control-plane
---

# discover

O runtime já persiste `AgenticRun`, invoca adapters fake e produz replay básico.
Faltava uma entidade de controle para steps independentes, orçamento, retry,
cancelamento, retomada, paralelismo dinâmico e revisão final.

Limites: local/CI, append-only, sem providers de modelo, AWS, bancos ou
mutação externa.
