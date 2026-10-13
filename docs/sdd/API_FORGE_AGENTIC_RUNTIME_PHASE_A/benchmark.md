---
sdd: 1
feature: API_FORGE_AGENTIC_RUNTIME_PHASE_A
phase: benchmark
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "d2aca50378ce41d1130ef054ec365ded4439cb7bf0df8d177cbbe76cf183417e"
baseline: fixed bounded scheduler without digest review
results:
  - artifact: sdd/API_FORGE_AGENTIC_RUNTIME_PHASE_A/evidence/runtime-tests.txt
    outcome: measured-by-test
    note: throughput de modelos reais depende do adapter aprovado
---
# benchmark

O scheduler local controla chamadas sem depender de um provider de modelo.
