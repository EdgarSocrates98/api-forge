---
sdd: 1
feature: API_FORGE_CYCLE12_PORTABLE_DIST
phase: contract
profile: standard
status: done
upstream:
  path: intent.md
  sha256: "905cc35dd17fe9d257878be2e0036403fed9b75a18e2801cd2f371943ec5658c"
covers:
  - packaged-data resolvers (env -> cwd -> repo-marker -> packaged)
  - pack_dir(domain) identifier-not-path; AF-KNOW-DOMAIN on traversal
  - evals verb + --dist install path in shared bootstrap
  - no resource resolution requires a checkout
  - writes into site-packages refused
---

# contract

Behavioral contract for the portable distribution slice of api-forge (Cycle 12).
