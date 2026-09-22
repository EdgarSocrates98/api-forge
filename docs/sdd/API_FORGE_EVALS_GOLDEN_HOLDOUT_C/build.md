---
sdd: 1
feature: API_FORGE_EVALS_GOLDEN_HOLDOUT_C
phase: build
profile: standard
status: done
upstream:
  path: plan.md
  sha256: "445e3f7867a2f117ad3874b226148cff44f004475c208a3254b1ba54b42da2ce"
tasks:
  - id: suite
    status: done
    evidence: sdd/API_FORGE_EVALS_GOLDEN_HOLDOUT_C/evidence/eval-tests.txt
  - id: gates
    status: done
    evidence: sdd/API_FORGE_EVALS_GOLDEN_HOLDOUT_C/evidence/eval-tests.txt
claims:
  - four initial eval cases cover contract, migration, performance and agentops
  - missing evidence produces BLOCKED
  - valid golden plus quality axes produces PASS
---

# build

Implementado em `apiforge.evals.suite`, `evals/cases/platform.yaml` e CLI.
