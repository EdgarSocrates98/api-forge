---
sdd: 1
feature: API_FORGE_HOST_PARITY_H
phase: discover
profile: standard
status: draft
approaches:
  - id: claim-100
    summary: declarar paridade total sem auditoria
    verdict: refused -- hooks e MCP variam por host
  - id: parity-audit
    summary: auditar layout e reportar limitações
    verdict: chosen -- honesto e verificável
chosen: parity-audit
---
# discover

Skills e agents foram espelhados, mas host runtimes não possuem a mesma superfície.
