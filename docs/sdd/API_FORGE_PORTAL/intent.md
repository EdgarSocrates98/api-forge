---
sdd: 1
feature: API_FORGE_PORTAL
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "17ce0e01ebacd4737b863a8b1a5bb33c5f1e951a8cb8ec6e9f896087935f3050"
problem: >
  O api-forge exige aprender verbos/flags antes de qualquer jornada;
  o Forge Portal oferece uma UI local opcional sobre os mesmos serviços
  e recibos, e o api-forge precisa do seu adapter + verbo `portal`.
success:
  - portal-http-surface
  - install-plan-confirm-apply
  - analyze-real-via-portal
  - named-refusals
  - assets-clone-e-wheel
out_of_scope:
  - segunda implementação de análise/contrato/evidence
  - launch de host sem TTY (retorna launch_command)
  - exposição fora de 127.0.0.1, TLS ou multiusuário
  - páginas especializadas novas no SPA (reuso das 11 existentes)
owner: api-forge-portal
---

# intent

Adapter `apiforge.portal_adapter` + verbo `apiforge portal` mapeando
`forge/PortalApi/1` nos serviços reais. Gate: análise real de API via
portal com case persistido.
