---
sdd: 1
feature: API_FORGE_AGENTIC_QUALITY_HOST_PARITY_G
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "42921945600bec5ad60f69641c41619e2ed9f13d11ad6fd50c5d7ceb74c5a75b"
problem: >
  Um agente pode declarar qualidade sem holdout ou paridade real entre Claude,
  Codex, Devin e Copilot.
success: [quality-aggregate, holdout-required, host-gaps-visible]
out_of_scope: [install-host-runtime, provider-login, model-benchmark]
owner: api-forge-agentops
---
# intent

Fechar o loop de avaliação agentica com um artefato único e conservador.
