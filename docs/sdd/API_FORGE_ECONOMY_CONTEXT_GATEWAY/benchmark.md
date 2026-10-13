---
sdd: 1
feature: API_FORGE_ECONOMY_CONTEXT_GATEWAY
phase: benchmark
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "0c218873deabac75642ed46a02e008c79f559e47edf033eea7a193e5e74bb301"
baseline: context resolve payload plus every required-evidence file read whole (evals/corpus/economy/baseline.json)
results:
  - artifact: sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/evidence/economy-eval.json
    outcome: measured
    note: "12/12 cases recall 1.0 = baseline; median byte reduction 0.477 (min 0.391, max 0.554) charging full expansion of every ref; capsules byte-identical across builds"
  - artifact: provider tokens
    outcome: unresolved
    note: no host transcript in the benchmark; bytes are not converted into tokens
---
# benchmark

Reduction is a conservative bound: the capsule side pays for expanding every
ref it carries. Fixtures are small, so the absolute savings grow with real
repository size; that extrapolation is not claimed here.
