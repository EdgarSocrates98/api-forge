---
sdd: 1
feature: API_FORGE_TOOL_ADAPTER_REGISTRY_B
phase: contract
profile: standard
status: done
upstream:
  path: intent.md
  sha256: "1d91feacea162b58208f1f2b0a877f59a84ae570ad8b8e2b6166e9fed1319bf6"
covers:
  - ToolAdapter/v1
  - agentops-tools-cli/v1
api_ir:
  input: existing TOOL_REGISTRY metadata
  output: typed adapter list or one adapter schema
---

# contract

`ToolAdapter/v1` declara nome, categoria, input/output schema, parser,
evidence producer, safety class, compact filter, capabilities, modes, runnable
e needs flags. Ferramenta desconhecida recusa com `AF-TOOL-ADAPTER-UNKNOWN`.
