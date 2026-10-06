---
sdd: 1
feature: API_FORGE_STEP11_TOKEN_ECONOMICS
phase: ship
profile: critical
status: done
deviations:
  - "the shipped pricing catalog is intentionally empty (entries: []); the
    project does not assert live provider prices -- callers declare their own
    catalog via --pricing, which keeps every price a declared fact"
  - automatic usage recording from runtime dispatch is deferred to the
    governor phase (phase 4); record-usage is the explicit ingress today
evidence:
  - docs/sdd/API_FORGE_STEP11_TOKEN_ECONOMICS/evidence/G1.txt
  - docs/sdd/API_FORGE_STEP11_TOKEN_ECONOMICS/evidence/G2.txt
  - docs/sdd/API_FORGE_STEP11_TOKEN_ECONOMICS/evidence/G3.txt
rollback: revert this commit; token_usage/*.jsonl rows are additive-only data
  and inert under v1 reads (older code never opens the new directory)
upstream:
  path: benchmark.md
  sha256: "d5a731c40ad55f222ea910378376dcc70c553af0dcb9e6a0c071a1d9dab768ab"
---

# ship
