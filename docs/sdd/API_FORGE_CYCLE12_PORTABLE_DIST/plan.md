---
sdd: 1
feature: API_FORGE_CYCLE12_PORTABLE_DIST
phase: plan
profile: standard
status: done
upstream:
  path: architecture.md
  sha256: "f7f4b2bd8f13915ef7a5a20a50f4ac8afa90c1a9e3ac75efba77ddf6763466fe"
tasks:
  - id: G1
    covers: [data-includes, evals-resolvers, artifact-wheel-test]
    test: sdd/API_FORGE_CYCLE12_PORTABLE_DIST/evidence/G1-artifact-wheel.txt
  - id: G2
    covers: [pack-dir-refusal, distribution-name]
    test: sdd/API_FORGE_CYCLE12_PORTABLE_DIST/evidence/G2-knowledge-mcp.txt
  - id: G3
    covers: [wheel-only-e2e]
    test: sdd/API_FORGE_CYCLE12_PORTABLE_DIST/evidence/G3-e2e.txt
---

# plan

Execution plan (retroactive record — work shipped via ecosystem review).
