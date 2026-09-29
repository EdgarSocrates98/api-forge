---
sdd: 1
feature: API_FORGE_FIELD_INTEGRITY_HARDENING
phase: ship
profile: critical
status: draft
upstream:
  path: benchmark.md
  sha256: "5cd75878f56c920ed0216353160e738f17e4f75aba7f2b5fd59cef31e71f6f7b"
deviations:
- clock-seam-utc-now-added-for-deterministic-tests
- git-head-read-only-at-seal
- release-gate-orphan-agent-mirror-preexisting
evidence:
- path: sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/evidence/field-tests.txt
  sha256: a5788f301ac0ee5bbc62bf71cef2f878a6a8e94559add8f864d9c863f0a40403
- path: sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/evidence/full-suite.txt
  sha256: 2721b73ed17920c183ff30474d7b012b56d9f886073fe27ef9ffd80a469ded00
---
# ship

Pre-registration is sealed by `docs/field/cycle.lock.json`, verification is bound to the annotation digest, verifier independence is enforced and H1 is decided only on a ready cycle. The field cycle is still unstarted: the owner pins the OpenTelemetry Demo commit, registers the corpus tasks and then runs the cycle.
