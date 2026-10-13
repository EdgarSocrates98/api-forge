---
sdd: 1
feature: API_FORGE_PRODUCT_DOCUMENTATION_RELEASE_H
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "966629263128651827f0f552aa1be0baa35a34c079abca46ba0f099903595cd6"
files: [README.md, docs/API_FORGE_EVOLUTION_MAP.md, docs/sdd]
decisions:
  - id: docs-follow-contracts
    decision: documentar somente capacidades presentes e gates verificáveis
    rollback: reverter documentação do release
  - id: external-boundary-explicit
    decision: separar core local de adapters externos em todos os textos
    rollback: manter documentação anterior até revisão
---
# architecture

O release finaliza orientação sem alterar a política offline-first.
