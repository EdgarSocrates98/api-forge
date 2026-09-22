---
sdd: 1
feature: API_FORGE_CONTRACT_INTELLIGENCE_DIGITAL_TWIN_D
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "d64c71577a9547ac1a4f2689819f921888d06b9ae4fb7731c3f6d90a063451ce"
covers:
  - ContractImpact/v1
  - TwinPlan/v1
  - TwinScenario/v1
  - TwinSimulation/v1
api_ir:
  input: contratos OpenAPI ou gRPC locais
  output: impacto versionado e plano/simulação offline com digests
---

# contract

`ContractImpact/v1`, `TwinPlan/v1`, `TwinScenario/v1` and `TwinSimulation/v1` are immutable, JSON-serializable outputs with protocol, digest, verdict, evidence and no-network proof.
