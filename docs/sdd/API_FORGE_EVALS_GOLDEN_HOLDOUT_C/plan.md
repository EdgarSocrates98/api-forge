---
sdd: 1
feature: API_FORGE_EVALS_GOLDEN_HOLDOUT_C
phase: plan
profile: standard
status: done
upstream:
  path: architecture.md
  sha256: "92f0e65ebb29c4c5df9c59bbb86c55d443867d708fa917e6e936f37650d9d979"
tasks:
  - id: suite
    covers: [declarative-eval-matrix, quality-score]
    test: sdd/API_FORGE_EVALS_GOLDEN_HOLDOUT_C/evidence/eval-tests.txt
    risk: low
    rollback: remove evals/suite.py
  - id: gates
    covers: [required-evidence-gate, mutation-holdout-digest]
    test: sdd/API_FORGE_EVALS_GOLDEN_HOLDOUT_C/evidence/eval-tests.txt
    risk: medium
    rollback: keep existing eval files only
---

# plan

Adicionar loader, result contract, mutation probe, matriz inicial e comandos
read-only `evals list`/`evals validate`.
