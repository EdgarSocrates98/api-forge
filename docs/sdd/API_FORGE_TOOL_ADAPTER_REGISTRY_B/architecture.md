---
sdd: 1
feature: API_FORGE_TOOL_ADAPTER_REGISTRY_B
phase: architecture
profile: standard
status: done
upstream:
  path: contract.md
  sha256: "e9f948f48fffaa4596959a775b303e9d15eed3a7a2274eda0c1dd64c063c86c0"
files:
  - src/apiforge/agentops/tools.py
  - src/apiforge/cli.py
  - tests/agentops/test_tools.py
decisions:
  - id: overlay
    decision: derivar adapters de TOOL_REGISTRY em tempo de consulta
    rollback: remover agentops.tools sem tocar run_tools
  - id: safety
    decision: network/credentials viram safety_class explícita
    rollback: retornar metadata original e manter policy gate
  - id: evidence
    decision: parser e evidence producer são obrigatórios no adapter
    rollback: marcar adapter como unresolved, nunca inferir parser
---

# architecture

O registry tipado é uma projeção read-only. Ele não instala, executa ou muda a
allowlist. Workflows usam o adapter para escolher ferramentas; `run_tools` e a
policy engine continuam sendo as autoridades de execução.
