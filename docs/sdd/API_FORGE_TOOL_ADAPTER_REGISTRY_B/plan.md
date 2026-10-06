---
sdd: 1
feature: API_FORGE_TOOL_ADAPTER_REGISTRY_B
phase: plan
profile: standard
status: done
upstream:
  path: architecture.md
  sha256: "8eda9b48328d748b8ffd6ad148e455e1873b634b869128b3135b0db4dd673cb6"
tasks:
  - id: typed-registry
    covers: [typed-tool-adapters, safety-classification]
    test: sdd/API_FORGE_TOOL_ADAPTER_REGISTRY_B/evidence/tool-tests.txt
    risk: low
    rollback: remove tools.py
  - id: cli
    covers: [host-readable-cli, evidence-producer-discovery]
    test: sdd/API_FORGE_TOOL_ADAPTER_REGISTRY_B/evidence/tool-tests.txt
    risk: low
    rollback: remove agentops tools commands
---

# plan

Adicionar camada tipada, dois comandos read-only e testes de paridade com os
doze adapters declarados no registry atual.
