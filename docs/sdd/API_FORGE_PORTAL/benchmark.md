---
sdd: 1
feature: API_FORGE_PORTAL
phase: benchmark
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "a0dda21ac8e199792798bf48f06cb7938ea926c50274ba6e70993fa2e6e6a3da"
baseline: "stdlib HTTPServer + assets estáticos; sem runtime adicional"
results:
  - "tests/test_portal_adapter.py: 20 testes em ~11s (inclui analyze_project real sobre fixture FastAPI)"
  - "servidor: sem dependências novas — stdlib only; adapter importa serviços já instalados"
  - "bundle: +1 módulo vendored (~700 LoC) + assets SPA já vendored; sem dep nova no pyproject"
---

# benchmark

Custo marginal: nenhum runtime extra, nenhuma dependência nova; o único
custo mensurável é a suíte de testes (~11s) e o tamanho do wheel
(assets vendored, ~100 kB comprimidos).
