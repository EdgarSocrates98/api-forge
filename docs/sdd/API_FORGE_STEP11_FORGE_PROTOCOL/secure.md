---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: secure
profile: critical
status: done
threat_model:
  - "forge as covert execution channel — submit persists a request; nothing
    executes, attaches are explicit links to governed TaskSpecs only"
  - "handoff as remote mutation — handoff writes a prepared record for a
    declared engine allowlist; delivery is out-of-band and human-gated"
  - "capability matrix as invented surface — descriptors derive from the
    declared contract/agent registry, never from model memory"
  - "risk bypass — gated risk classes need --acknowledge-risk; the flag is
    recorded on the persisted task row"
  - "evidence fabrication — bundles contain observed artifacts only;
    missing governed links and missing ledger rows are named in unresolved"
  - "policy tampering — malformed forge_protocol.yaml refuses AF-FORGE-POLICY"
  - "task-id injection — ids match the governed pattern and the store
    refuses unreadable/invalid persisted rows with AF-FORGE-STORE"
upstream:
  path: verify.md
  sha256: "039e69df7d0826194d5b0f0cdc3301c51c9513ddb09ef0ace480f685c4fb6b48"
---

# secure

The surface is a controlled boundary: validation at submit, explicit
attach, read-only projections, prepared-not-delivered handoffs. MCP
exposes no mutation verbs. Case/ledger integrity is inherited from the
governed stores — the forge layer writes only under `.apiforge/forge/`.
