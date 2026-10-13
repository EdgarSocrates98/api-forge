---
sdd: 1
feature: API_FORGE_SECURITY_RESILIENCE_GATE_F
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "d2b4338d53c3c5cd995b3fef1ee6242c35fe0c393a668930765cd52c689f2350"
covers: [ApiSafetyAssessment/v1]
api_ir:
  input: map of required controls as true, false or unknown
  output: ready, review or blocked with control lists
---
# contract

`None` significa declaração ausente e resulta em `review`; `False` é falha explícita e resulta em `blocked`.
