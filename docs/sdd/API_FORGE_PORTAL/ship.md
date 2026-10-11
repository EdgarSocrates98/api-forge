---
sdd: 1
feature: API_FORGE_PORTAL
phase: ship
profile: standard
status: draft
upstream:
  path: benchmark.md
  sha256: "7ae3fe8a4ad0943aadce9ee66a30d8e12b2429aa23af0648a8551cced45db03a"
deviations:
  - páginas especializadas Angular (contracts/architecture/evidence/agentops dedicadas) ficam para a onda de polish do forge-portal — a task `analyze` já cobre o gate da FASE 4 com case persistido
evidence:
  - tests/test_portal_adapter.py (20 testes verdes)
  - docs/reference/command-rationale.json (verbo portal)
  - docs/learn/recipes/portal.md
  - regen_docs: commands.generated.json atualizado, 0 undocumented
hypothesis_outcome: confirmed
---

# ship

`apiforge portal` abre a UI local com token de sessão; install lifecycle,
hosts, MCP, catálogos, tasks seguras (incl. análise real de API), graph e
docs search operam sobre os serviços reais — mesma arquitetura provada no
spark-forge-aws, negócio do api-forge intacto.
