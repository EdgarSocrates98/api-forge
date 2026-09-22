---
sdd: 1
feature: API_FORGE_OBSERVABILITY_OPERATIONAL_READINESS_D
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "e0faaf13ab1f2d66855734e34621b594b354c6b9c4ef8b7cbcc3dec1de158cc7"
problem: >
  Um agente não consegue distinguir configuração incompleta, bloqueio de
  segurança e export pronto antes de chegar ao adapter host.
success: [provider-preflight, approval-aware-status, network-free]
out_of_scope: [resolver-segredos, enviar-telemetria, criar-contas-vendor]
owner: api-forge-observability
---
# intent

Oferecer uma resposta de prontidão operacional determinística para cada provider.
