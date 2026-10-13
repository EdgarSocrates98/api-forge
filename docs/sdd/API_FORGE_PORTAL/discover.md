---
sdd: 1
feature: API_FORGE_PORTAL
phase: discover
profile: standard
status: draft
approaches:
  - id: cli-wrapper
    note: portal chama o CLI via subprocess — duplica camada, perde tipos e recusa estruturada
  - id: import-services
    note: adapter importa install.service, integrations.hosts, application.analyze e graphview — mesmos serviços do CLI/TUI/MCP
  - id: new-engine
    note: reimplementar lógica no servidor web — proibido pelo prompt (nunca um segundo motor)
chosen: import-services
---

# discover

O Forge Portal compartilhado (forge-portal, `portal_core/forge_portal.py`)
já provou a arquitetura no spark-forge-aws: servidor stdlib em
`127.0.0.1` + token de sessão, envelope `forge/PortalApi/1`, adapter por
forja mapeando operações nos serviços reais. A escolha para o api-forge
é importar os serviços (`install.service`, `integrations.hosts`,
`application.analyze`, `graphview`) — sem subprocess, sem reimplementação.
