---
sdd: 1
feature: API_FORGE_EVALS_GOLDEN_HOLDOUT_C
phase: intent
profile: standard
status: done
upstream:
  path: discover.md
  sha256: "19aaadbfbb4b0110fd71b6d2fa0906431c68636848b42d62a13398724865a837"
problem: >
  Sem uma matriz de evals comum, regressões de evidência, falso DONE e perda de
  qualidade após compactação podem passar despercebidas.
success:
  - declarative-eval-matrix
  - required-evidence-gate
  - mutation-holdout-digest
  - quality-score
out_of_scope:
  - execução de modelos
  - benchmark de custo real de providers
  - geração automática de fixtures reais
owner: api-forge-quality
---

# intent

Criar uma base de avaliação offline, versionada e reproduzível para todos os
subsystems do API Forge.
