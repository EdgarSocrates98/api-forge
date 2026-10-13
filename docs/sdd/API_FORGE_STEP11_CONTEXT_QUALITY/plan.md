---
sdd: 1
feature: API_FORGE_STEP11_CONTEXT_QUALITY
phase: plan
profile: critical
status: done
upstream:
  path: architecture.md
  sha256: "72c76bc5baddb3ea6363cf5ef633644196e9495211353e8f37d7f6a65fb3463d"
tasks:
  - id: G1
    covers: [context-quality-contracts, context-quality-engine]
    test: sdd/API_FORGE_STEP11_CONTEXT_QUALITY/evidence/G1.txt
  - id: G2
    covers: [context-quality-evals, minimum-sufficient-context]
    test: sdd/API_FORGE_STEP11_CONTEXT_QUALITY/evidence/G2.txt
  - id: G3
    covers: [role-context-v2]
    test: sdd/API_FORGE_STEP11_CONTEXT_QUALITY/evidence/G3.txt
---

# plan

1. Contracts first (closed vocabularies, basis enforcement) + registry.
2. Pure engine functions; no I/O besides the ledger replay.
3. Sufficiency as a one-pass fixpoint over `evaluate`.
4. v2 yaml schema with additive `policies:`; loader accepts v1 and v2.
5. CLI + eval wiring, AF codes in `docs/catalog-contract.md`.
