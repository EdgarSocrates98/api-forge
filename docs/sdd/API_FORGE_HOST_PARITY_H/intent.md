---
sdd: 1
feature: API_FORGE_HOST_PARITY_H
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "4274785069ff1817d98bca1bb2535f642a7207d49aa7e1a79dafe2a68c0d16ab"
problem: >
  Usuários precisam saber o que funciona em Claude, Codex, Devin e Copilot sem
  confundir core compartilhado com integração específica do host.
success: [host-layout-audit, honest-limitations, shared-core-proof]
out_of_scope: [host-installation, provider-login, ui-parity]
owner: api-forge-agentops
---
# intent

Auditar prontidão do repositório para cada host.
