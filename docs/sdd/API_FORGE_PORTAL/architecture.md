---
sdd: 1
feature: API_FORGE_PORTAL
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "99fdfc5314fa4c928c58434b233826e1042fa0a624deafa631c44fea6cf7a81b"
files:
  - src/apiforge/portal_adapter.py
  - src/apiforge/cli_portal.py
  - src/apiforge/_forge_portal.py  # vendored — canonical: forge-portal/portal_core
  - portal/assets/                  # vendored SPA — canonical: forge-portal/dist
  - tests/test_portal_adapter.py
  - pyproject.toml                  # force-include portal/assets → apiforge/portal_assets
decisions:
  - id: import-not-subprocess
    call: adapter chama service.install/status/doctor/repair/uninstall/mcp_verify, hosts.ai_flow e analyze_project diretamente
    rollback: remover o módulo; nenhum serviço foi alterado
  - id: ledger-beats-doctor
    call: ledger unverified+vazio → NOT_INSTALLED mesmo com doctor 'broken' (checks falham por assets ausentes, não por dano)
    rollback: mapear doctor cru; mentiria "degradado" em workspace virgem
  - id: tasks-safe-verbs
    call: intent → verbos fixos (mcp_verify, doctor, status, analyze, graph, skills, agents); resto → AF-PORTAL-AMBIGUOUS
    rollback: expor só status/health
  - id: workspace-sandbox
    call: args de analyze resolvem dentro do workspace; escape → AF-PORTAL-INPUT na execução (task refused)
    rollback: aceitar caminho absoluto — viola a fronteira
  - id: host-launch-command-only
    call: /hosts/launch devolve launch_command; portal nunca executa binário (sem TTY)
    rollback: subprocess — proibido, o host abriria num processo-filho órfão
---

# architecture

Mesmo shape do adapter do spark-forge-aws: `ApiForgePortal(fp.PortalAdapter)`
registra operações `forge/PortalApi/1`; `_forge_portal.PortalServer`
(HTTP stdlib, sessão por token, SSE) serve os assets vendored. Nenhuma
lógica de negócio no servidor — todo campo vem de um serviço real.
