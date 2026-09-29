---
sdd: 1
feature: API_FORGE_FIELD_INTEGRITY_HARDENING
phase: secure
profile: critical
status: draft
upstream:
  path: verify.md
  sha256: "a325cd80232f502336592416417619ccc4e995b9e257ee293da6ed6285a9f909"
threat_model: docs/security/threat-model-mvp.md
---
# secure

Offline only. Humans are accepted only as `human:sha256:<64 hex>`; raw names are refused (`AF-FIELD-ACTOR-INVALID`). `field verify` still never echoes human labels. The only subprocess is a read-only `git rev-parse HEAD` with fixed argv, no shell and a 5s timeout; failure leaves `git_commit` null. The lock is tamper-evident, not tamper-proof: a consistent rewrite of corpus and lock is visible only in git history, as documented in `docs/field/README.md`.
