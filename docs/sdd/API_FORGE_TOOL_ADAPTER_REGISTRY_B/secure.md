---
sdd: 1
feature: API_FORGE_TOOL_ADAPTER_REGISTRY_B
phase: secure
profile: standard
status: done
upstream:
  path: verify.md
  sha256: "403b2a34136a4f427b9e5d8388cf50cf2c6ed3d298b43f9eca3109b897eabcd0"
threat_model: docs/security/threat-model-mvp.md
---

# secure

O registry é somente leitura. Network, credentials e load tools permanecem
explicitamente classificados; nenhum adapter novo obtém execução por existir no
catálogo.
