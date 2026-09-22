---
sdd: 1
feature: API_FORGE_CONTRACT_INTELLIGENCE_DIGITAL_TWIN_D
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "e7c828534d3546c1e1bc3c2e79bc6cc075e1d960143a0e2d68db76206da7385f"
tasks:
  - id: models
    covers: [unified-contract-impact, offline-digital-twin]
    test: sdd/API_FORGE_CONTRACT_INTELLIGENCE_DIGITAL_TWIN_D/evidence/contract-intel-tests.txt
    risk: low
    rollback: remover contract_intel/models.py
  - id: adapters-and-cli
    covers: [deterministic-fault-scenarios, no-network-proof]
    test: sdd/API_FORGE_CONTRACT_INTELLIGENCE_DIGITAL_TWIN_D/evidence/contract-intel-tests.txt
    risk: medium
    rollback: remover comandos contract-intel
---

# plan

1. Add provider-neutral impact and twin models.
2. Adapt OpenAPI and gRPC loaders behind one service.
3. Expose CLI commands for impact and twin plan/simulation.
4. Verify deterministic scenarios, digests and network prohibition.
