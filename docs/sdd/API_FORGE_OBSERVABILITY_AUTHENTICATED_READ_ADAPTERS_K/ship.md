---
sdd: 1
feature: API_FORGE_OBSERVABILITY_AUTHENTICATED_READ_ADAPTERS_K
phase: ship
profile: standard
status: draft
upstream:
  path: benchmark.md
  sha256: "9d2d616ef46525edd8d310039052282670a7b75532c806ad818a842391050dc1"
deviations: [fake-transport-only]
evidence:
  - path: sdd/API_FORGE_OBSERVABILITY_AUTHENTICATED_READ_ADAPTERS_K/evidence/adapter-tests.txt
    sha256: "364a6865c0ecf9c9033ce3c8d9ccc8e5f528705e31c7d03b3ec1461619120333"
---
# ship

Adapter read-only publicado; implementação de transporte real depende de broker e aprovação.
