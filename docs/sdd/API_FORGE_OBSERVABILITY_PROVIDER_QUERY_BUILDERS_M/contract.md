---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "dabda6a63ee48327c10170b131b7d5e6416a3f8de67c04c47f53525b73516dd2"
covers: [build_provider_params/v1]
api_ir:
  input: ReadPlan/v1
  output: mapping of provider query parameters without secrets
---
# contract

`build_provider_params` é puro, determinístico e não resolve credenciais nem executa rede.
