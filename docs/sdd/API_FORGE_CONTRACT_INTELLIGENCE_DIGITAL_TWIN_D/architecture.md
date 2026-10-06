---
sdd: 1
feature: API_FORGE_CONTRACT_INTELLIGENCE_DIGITAL_TWIN_D
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "bb5a009ddafefd18a040e34355e3fe89efe74b8a02fa23b42b203d27f3197094"
files:
  - src/apiforge/contract_intel/models.py
  - src/apiforge/contract_intel/service.py
  - src/apiforge/cli.py
  - tests/contract_intel/test_contract_intel.py
decisions:
  - id: adapter-reuse
    decision: reutilizar diff OpenAPI e compatibilidade gRPC existentes
    rollback: remover o namespace contract_intel sem alterar os motores
  - id: no-network
    decision: Digital Twin só planeja e simula dados locais
    rollback: manter apenas o planner caso simulação seja desativada
---

# architecture

`contract_intel.service` adapts existing OpenAPI diff and gRPC compatibility engines. The Digital Twin is a pure planner/simulator: it consumes contract digests, declares dependencies and scenarios, and never starts a process or calls HTTP, AWS or databases.
