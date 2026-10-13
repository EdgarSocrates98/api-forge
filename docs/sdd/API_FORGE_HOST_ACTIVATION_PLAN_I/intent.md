---
sdd: 1
feature: API_FORGE_HOST_ACTIVATION_PLAN_I
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "c93405a594a17fc07ae14f6367f8e9786fdb6183004d4fb5f453fe705c45473e"
problem: >
  Usuários precisam ativar o API Forge em seus hosts sem mutação invisível,
  instalação remota ou promessa de capacidades inexistentes.
success: [activation-plan, approval-gate, host-limitations]
out_of_scope: [silent-install, config-write, remote-download]
owner: api-forge-agentops
---
# intent

Gerar instruções de ativação específicas e seguras.
