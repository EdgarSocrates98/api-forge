---
sdd: 1
feature: API_FORGE_CYCLE12_PORTABLE_DIST
phase: discover
profile: standard
status: done
chosen: packaged-data-layer
approaches:
  - id: packaged-data-layer
    summary: force-include `_data/{knowledge,evals,tests/fixtures}` +
      host_assets/portal_assets na wheel, resolvidos via
      `importlib.resources` (cwd → checkout-marker → packaged)
    verdict: accepted -- provado por test_artifact_contents na wheel real
      e E2E descartavel (venv limpa, `apiforge knowledge list` = 40 packs)
  - id: checkout-only-runtime
    summary: manter evals/knowledge fora da wheel, exigindo clone
    verdict: refused -- viola §7.3 (usuario final nao clona source)
retroactive: true
---

# discover

Registro retroativo da fatia api-forge do Cycle 12 (distribuicao
universal): a fatia entrou pela trilha de review do ecossistema
(the-forge baseline.md, 14 rodadas) antes da abertura de um feature dir
SDD proprio. Este feature documenta as decisoes e liga a evidencia.
