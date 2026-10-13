---
sdd: 1
feature: API_FORGE_STEP11_TRUST_PLANE
phase: plan
profile: critical
status: done
upstream:
  path: architecture.md
  sha256: "923c12f8bea3fa8d4498c873e55689731aebc5c3bec48102b61c1c598503a661"
tasks:
  - id: G1
    covers: [trust-contracts, trust-plane, taint-propagation]
    test: sdd/API_FORGE_STEP11_TRUST_PLANE/evidence/G1.txt
  - id: G2
    covers: [tool-authorization, memory-security-v2]
    test: sdd/API_FORGE_STEP11_TRUST_PLANE/evidence/G2.txt
  - id: G3
    covers: [memory-retrieval-v2, invalidation-triggers, checkpoint-parity]
    test: sdd/API_FORGE_STEP11_TRUST_PLANE/evidence/G3.txt
---

# plan

1. Contracts + widened literals first (additive), registry + doc files.
2. `trust/` pure functions; yaml policy as data.
3. Extract the §14 gate pipeline; store rewires; quarantine log + review.
4. Ranking + advisory invalidation; checkpoint parity test.
5. CLI (`memory rank|quarantine-list|quarantine-resolve`) + MCP parity tools.
6. Catalog codes, contract docs, guide §18 distinction, README rows.
