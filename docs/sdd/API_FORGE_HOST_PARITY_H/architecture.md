---
sdd: 1
feature: API_FORGE_HOST_PARITY_H
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "c01bb3ae896d8b1251fd057f201ff6762d87530a2a893a140bc3f73a258579bc"
files: [src/apiforge/agentops/parity.py, src/apiforge/cli.py, docs/HOST_PARITY.md]
decisions:
  - id: report-boundary
    decision: reportar limitações em vez de adaptar host invisivelmente
    rollback: remover auditoria mantendo AGENTS.md e CLAUDE.md
---
# architecture

O auditor lê o layout e não instala hooks nem altera configurações do usuário.
