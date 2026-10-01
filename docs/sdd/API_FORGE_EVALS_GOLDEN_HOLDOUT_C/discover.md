---
sdd: 1
feature: API_FORGE_EVALS_GOLDEN_HOLDOUT_C
phase: discover
profile: standard
status: done
approaches:
  - id: model-only
    summary: avaliar respostas livres de modelos
    verdict: refused -- não é determinístico nem reproduzível no CI
  - id: declarative-local
    summary: matriz declarativa com goldens, evidência e mutation/holdout
    verdict: chosen -- funciona sem provider e mede decisão verificável
chosen: declarative-local
---

# discover

O repositório já possuía evals declarativos isolados por capacidade. Faltava uma
matriz transversal com vocabulário fechado, requisitos de prova e probes de
mutação/holdout reutilizáveis por runtime, migração, performance e AgentOps.
