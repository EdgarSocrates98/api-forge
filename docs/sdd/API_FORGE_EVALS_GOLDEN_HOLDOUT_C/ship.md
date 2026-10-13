---
sdd: 1
feature: API_FORGE_EVALS_GOLDEN_HOLDOUT_C
phase: ship
profile: standard
status: draft
upstream:
  path: benchmark.md
  sha256: "0793b7ec1189760d0516e84295c48d79ffb38203a2481d797d40047d51592b5c"
deviations:
  - "No real model/provider transcript is included."
evidence:
  - path: sdd/API_FORGE_EVALS_GOLDEN_HOLDOUT_C/evidence/eval-tests.txt
    sha256: "9fc87118a3bc08264b65503f77dc9b407e0bb95d7d197280d40bbf0e11aadd2d"
---

# ship

Harness local pronto para receber goldens reais e evals por host/modelo.
