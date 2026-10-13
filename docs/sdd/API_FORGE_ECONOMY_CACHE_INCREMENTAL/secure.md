---
sdd: 1
feature: API_FORGE_ECONOMY_CACHE_INCREMENTAL
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "de87968b0d1d8c2d719f09ff3fb4650e55c85ce61c54447e35b8fcb9305f76c7"
threat_model: docs/security/threat-model-mvp.md
---
# secure

git is invoked with argument arrays only (`rev-parse`, `diff --name-status`, `show`), never a shell, never a mutating command. Shared-tier objects are re-hashed on every read; a tampered object is a miss. Entries carry root-relative paths only. `context gc` deletes only with `--apply` and only under `.apiforge/cache`, `.apiforge/ctx` and the configured cache home.
