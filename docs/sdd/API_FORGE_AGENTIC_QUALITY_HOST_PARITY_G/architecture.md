---
sdd: 1
feature: API_FORGE_AGENTIC_QUALITY_HOST_PARITY_G
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "82525f98e07fbb39bfeca35361f7cdaa22c2745005bbc62fcb901951d85264f6"
files: [src/apiforge/quality.py, src/apiforge/contracts/stubs.py, src/apiforge/agentops/parity.py]
decisions:
  - id: preserve-case-verdicts
    decision: contar PASS, REVIEW e BLOCKED separadamente
    rollback: remover agregador
  - id: parity-is-evidence
    decision: tratar hosts não prontos como gap, não como falha de modelo
    rollback: reportar somente qualidade dos evals
---
# architecture

O agregador recebe resultados produzidos por evals e o mapa factual do host, sem executar subagents.
