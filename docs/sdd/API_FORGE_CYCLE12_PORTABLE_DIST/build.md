---
sdd: 1
feature: API_FORGE_CYCLE12_PORTABLE_DIST
phase: build
profile: standard
status: done
upstream:
  path: plan.md
  sha256: "b16d70a30d90ce648204237fe53cf44116c9e510c2ca69af9c6c5b94f2a1ae2f"
tasks:
  - data-includes
  - evals-resolvers
  - pack-dir-refusal
  - distribution-name
  - artifact-wheel-test
claims:
  - wheel carries _data/{knowledge,evals,tests/fixtures} + host/portal assets
  - evals resolve without checkout; .. refused
  - domain traversal refused with AF-KNOW-DOMAIN
---

# build

Build report: implementation landed in commit d014d3b and predecessors.
