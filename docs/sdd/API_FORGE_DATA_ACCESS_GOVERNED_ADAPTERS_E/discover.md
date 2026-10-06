---
sdd: 1
feature: API_FORGE_DATA_ACCESS_GOVERNED_ADAPTERS_E
phase: discover
profile: standard
status: draft
approaches:
  - id: live-probe
    summary: conectar automaticamente em Redis, Mongo, Dynamo ou Neptune
    verdict: refused -- exige credenciais, rede e impacto externo
  - id: static-governance
    summary: avaliar DataAccessIR e mutações declaradas antes do adapter
    verdict: chosen -- seguro e útil sem ambiente real
chosen: static-governance
---
# discover

Os scanners já extraem call sites; faltava governar prontidão, credenciais e mutações por banco.
