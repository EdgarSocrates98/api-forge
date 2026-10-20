---
sdd: 1
feature: API_FORGE_CYCLE12_PORTABLE_DIST
phase: intent
profile: standard
status: done
risk_class: medium
problem: runtime nao funcionava instalado via wheel sem checkout —
  evals/knowledge/fixtures fora do pacote, `<domain>` aceitava paths
  arbitrarios, `forge.json.distribution` apontava pacote homonimo
success: "wheel 0.1.2 carrega `_data/{knowledge,evals,tests/fixtures}`
  + host/portal assets; resolvers env→cwd→marker→packaged com `..`
  recusado; `pack_dir` recusa traversal (AF-KNOW-DOMAIN); distribution
  name confere com pyproject; artifact test constrói a wheel real"
out_of_scope:
  - publicacao real no PyPI (Fase G — credenciais)
  - matriz Windows/macOS (sem runners)
upstream:
  path: discover.md
  sha256: "20878cc099fd5a0723df8d44a34f2e683cab645a743454f857dafb81bbff46f0"
---

# intent

Fechamento retroativo: a implementacao ja foi verificada (23 testes
knowledge, artifact wheel tests, 122 knowledge/MCP tests); este feature
registra a decisao no SDD como o contrato do repo exige para mudancas
comportamentais.
