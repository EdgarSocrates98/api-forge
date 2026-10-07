---
sdd: 1
feature: API_FORGE_STEP11_MCP_SURFACE
phase: secure
profile: critical
status: done
threat_model:
  - disclosure as covert capability drop — unclassified tasks keep the
    full surface explicitly; declared names absent from the registry are
    named in unresolved
  - benchmark as side-effect — samples are read-only tools on an isolated
    temp root; nothing mutates the caller's ledgers
  - audit as fabrication — size/dup claims are observed-measured only;
    shape suspicions stay hypothesis and say why
  - policy tampering — malformed threshold/disclosure/sample files refuse
    with AF-MCP-*-POLICY, never silently clamped
upstream:
  path: verify.md
  sha256: "9ae4cf963015ac6a22b5747be0767d284156965d263b80d61f14fca35d6e156b"
---

# secure

Read-only over the registry and an isolated root. The new verbs mutate
nothing; the disclosure advisory cannot hide capability.
