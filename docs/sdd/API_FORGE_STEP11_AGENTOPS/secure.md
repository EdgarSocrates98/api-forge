---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: secure
profile: critical
status: done
threat_model:
  - secret leakage through reports — inspect emits counts, ref uris and
    evidence hashes only; payloads never enter findings
  - fabricated certainty — the contract validator refuses unresolved
    metrics carrying values and unresolved metrics without a named basis
  - silent detector failure — detectors lacking prerequisites (undeclared
    risk, empty ledgers, absent policy) land in unresolved or refuse with
    AF-AGENTOPS-WASTE-POLICY
  - policy tampering — thresholds come from the versioned rules file; a
    malformed override is refused, not clamped silently
  - mutation surface — all three verbs are read-only projections; MCP
    exposes the same three read tools
upstream:
  path: verify.md
  sha256: "12e92b8305454238ca57252648cb2d691c13c699dee29ec1f8ecf8cd13a8aac9"
---

# secure

Read-only over local ledgers. No provider calls, no payload echo, no new
network surface.
