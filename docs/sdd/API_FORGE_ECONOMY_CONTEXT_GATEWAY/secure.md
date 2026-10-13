---
sdd: 1
feature: API_FORGE_ECONOMY_CONTEXT_GATEWAY
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "2762b678d859918e7315ac570ed87aff4e96254617897ad32f89d11a6c56d3e6"
threat_model: docs/security/threat-model-mvp.md
---
# secure

`context expand` accepts only `ctx://sha256/<64 lowercase hex>` and resolves
inside `<root>/.apiforge/ctx`, so a ref cannot traverse paths. Objects are
re-hashed on every read; a mismatch refuses with `AF-CTX-HASH-MISMATCH` and
returns no content. The store only holds copies of files already inside the
analyzed root. No network, provider SDK or consumer-code execution.
