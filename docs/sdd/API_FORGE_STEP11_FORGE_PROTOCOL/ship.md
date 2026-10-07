---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: ship
profile: critical
status: done
deviations:
  - "kernel extraction stays analysis-only per §49 — the boundary doc records the seam without splitting the runtime"
  - "handoff delivery is out-of-band — ForgeHandoff records are prepared, never transmitted; no network transport exists"
  - "forge does not dispatch work — submit persists intent and attach links governed execution; no agent runs through the surface"
evidence:
  - docs/sdd/API_FORGE_STEP11_FORGE_PROTOCOL/evidence/G1-focused-tests.txt
  - docs/sdd/API_FORGE_STEP11_FORGE_PROTOCOL/evidence/G2-evals.txt
  - docs/sdd/API_FORGE_STEP11_FORGE_PROTOCOL/evidence/G3-gates.txt
rollback: "revert this commit; all modules, verbs, tools and docs are
  additive — older clients never call forge verbs and the governed
  runtime is unchanged"
upstream:
  path: benchmark.md
  sha256: "9da3b303e6bafed72e66e2aaa3f44499610ab6141373c4814d27eb9420cf8fec"
---

# ship

Phase 10 delivered: a versioned public boundary over the governed
runtime, eleven refusal codes with honest gates, evidence bundles with
explicit unresolved lists, prepared handoff records for declared peers
and the §49 kernel-boundary analysis — all additive, all deterministic.
