---
sdd: 1
feature: API_FORGE_CYCLE12_PORTABLE_DIST
phase: ship
profile: standard
status: done
upstream:
  path: benchmark.md
  sha256: "c21265f2f4deb177cce8dc5b45a0341230c399e66d146629565281d21340c4dc"
deviations:
  - feature dir created retroactively after ecosystem review rounds
evidence:
  - docs/sdd/API_FORGE_CYCLE12_PORTABLE_DIST/verify.md
  - the-forge docs/cycle12/baseline.md
hypothesis_outcome: confirmed — wheel-only install operates without checkout
---

# ship

Ship record. Pending cycle items (PyPI publish, Win/macOS matrix) live in the ecosystem baseline, outside this feature scope.
