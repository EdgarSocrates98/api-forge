---
sdd: 1
feature: API_FORGE_ECONOMY_CACHE_INCREMENTAL
phase: ship
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "7cd96a3671d340d9ef2cabd3f898eb6b92e1ecd7ef8944e94b8174874722cc68"
deviations:
- selection-cached-not-capsule
- delta-file-level-conservative
- l5-l7-declared-disabled
evidence:
- path: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-eval.json
  sha256: 0a4b827362984aef3e57feed5efb73b8f71cb12274c5f26eaa6b95bd2120ba7a
- path: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
  sha256: ad90213d6379d3ac29650a5a52beeadc7c21e3d0fde945047fa341cdf35391d9
---
# ship

Ready for review. The capsule envelope is recomposed on every call (its fingerprint changes with any analyzed input); only the evidence selection is cached. `context delta` maps files conservatively while the cache probes slices and JSON pointers. Knowledge, routing and validation layers are declared but disabled until a caller exists; model-response caching is disabled.
