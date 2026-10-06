---
sdd: 1
feature: API_FORGE_EVOLUTION1_GOVERNED_BUDGETS
phase: build
profile: critical
status: done
upstream:
  path: plan.md
  sha256: "609861f8c9646def29a47be8155b152e836b634e2687618972159de6d1db6449"
tasks:
  - id: G1
    status: done
    evidence: sdd/API_FORGE_EVOLUTION1_GOVERNED_BUDGETS/evidence/G1.txt
  - id: G2
    status: done
    evidence: sdd/API_FORGE_EVOLUTION1_GOVERNED_BUDGETS/evidence/G2.txt
  - id: G3
    status: done
    evidence: sdd/API_FORGE_EVOLUTION1_GOVERNED_BUDGETS/evidence/G3.txt
claims:
  - hierarchical limits are evaluated before append
  - stop, unresolved and deduplicated outcomes remain distinct
  - token usage is never inferred from bytes
---

# build

Wave 2 adds a deterministic hierarchical budget plane over existing measured
economy records. It does not call a provider or mutate an external system.
