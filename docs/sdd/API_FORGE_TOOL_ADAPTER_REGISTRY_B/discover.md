---
sdd: 1
feature: API_FORGE_TOOL_ADAPTER_REGISTRY_B
phase: discover
profile: standard
status: done
approaches:
  - id: duplicate-registry
    summary: criar catálogo paralelo de ferramentas
    verdict: refused -- gera drift com run_tools
  - id: typed-overlay
    summary: camada tipada sobre TOOL_REGISTRY e TOOLS existentes
    verdict: chosen -- mantém allowlist e compatibilidade
chosen: typed-overlay
---

# discover

O API Forge já possui `TOOL_REGISTRY`, argv allowlist, parsers e gates de alvo.
Faltava um contrato consumível por agentes e workflows que reunisse capability,
schema, safety class, parser, compactação e evidence producer.
