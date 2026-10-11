---
sdd: 1
feature: API_FORGE_PORTAL
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "f2c8c0a63ad646ff3b57fdc9f09751976ab533f5dc1363ed921ad38846e38bd0"
covers:
  - AC1: bootstrap sem sessão → 403; com sessão → descriptor+health NOT_INSTALLED num ledger vazio
  - AC2: installation plan/apply exige plan_token+confirm; recibo = install-ledger.json real
  - AC3: /skills e /agents servem o catálogo canônico (.agents/skills, agents/ ou host_assets do wheel)
  - AC4: toda mutação exige confirm explícito; plan_token divergente → PORTAL-PLAN-STALE
  - AC5: GET /graphs sem grafo → availability.no_graph com unlock `apiforge graph build`
  - AC6: intent ambígua → AF-PORTAL-AMBIGUOUS com safe_verbs; path fora do workspace → AF-PORTAL-INPUT
  - AC7: task analyze roda analyze_project e persiste case.json com case_id e artifacts hashados
  - AC8: health mapeia vocabulário real (healthy→INSTALLED/ACTIVE/VERIFIED; broken+ledger vazio→NOT_INSTALLED)
---

# contract

Superfícies: `apiforge portal [--no-browser] [--port N] [--root DIR]`
(Typer, help com why/when); módulos `apiforge.portal_adapter` e
`apiforge._forge_portal` (vendored, byte-identical ao canonical
forge-portal); assets `portal/assets/` (clone) → `apiforge/portal_assets/`
(wheel force-include). Refusal codes: `AF-PORTAL-*` + `PORTAL-*` do core.
