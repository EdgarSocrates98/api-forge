---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N
phase: discover
profile: standard
status: draft
approaches:
  - id: direct-core-http
    summary: abrir sockets e resolver credenciais no núcleo
    verdict: refused -- viola isolamento e governança
  - id: host-owned-requester
    summary: validar endpoint e delegar HTTP ao host
    verdict: chosen -- permite integração sem secrets no core
chosen: host-owned-requester
---
# discover

Os query builders estavam prontos, mas faltava uma fronteira segura para requesters HTTP reais.
