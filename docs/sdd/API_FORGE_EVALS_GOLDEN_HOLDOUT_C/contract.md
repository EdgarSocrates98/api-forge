---
sdd: 1
feature: API_FORGE_EVALS_GOLDEN_HOLDOUT_C
phase: contract
profile: standard
status: done
upstream:
  path: intent.md
  sha256: "2d9a8e4bf9c5ea3cc3064e50128c469565f65c2ed446ea2dbd8005b7f1ca8380"
covers:
  - EvalCase/v1
  - EvalResult/v1
  - evals-cli/v1
api_ir:
  input: YAML case matrix and observed evidence/axes
  output: PASS, REVIEW or BLOCKED with score and holdout digest
---

# contract

Cada `EvalCase` possui id único, domain, input, expected, required_evidence,
mutation e quality_axes. `EvalResult` registra verdict, score, gaps, failed
axes e digest do holdout. Evidência ausente nunca vira PASS.
