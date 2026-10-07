---
sdd: 1
feature: API_FORGE_STEP11_TRUST_PLANE
phase: secure
profile: critical
status: done
upstream:
  path: verify.md
  sha256: "c0199254fd3870f74dbe62ed2fa93bbe579e923e4c7a4d75ec867b468a4cef5d"
threat_model:
  - direct/indirect injection — payload text is data on every surface; instruction_authority is contract-enforced (system/governed_policy only)
  - tool-output and MCP injection — tool_result/mcp_response boundaries carry tool_output taint; propagation cannot clear it without evidence
  - memory poisoning — §14 gates reject untrusted/model origins and quarantine borderline trust; quarantined rows never reach retrieval
  - evidence poisoning — verification lift requires caller evidence_refs and raises trust at most one tier above the weakest source
  - privilege escalation / confused deputy — allowlist-first authorization; missing subject/tool, denied tool or excess risk all deny with cataloged codes
  - cross-task contamination — environment fingerprints filter retrieval; §16 triggers flag stale-environment records
  - unsafe mutation — everything is append-only; quarantine release re-runs gates, so a reviewer cannot bypass them
---

# secure

Agentic Security v2 lands as contracts and deterministic functions, not
prompt-level advice. The rule DATA IS NOT INSTRUCTION is enforced by the
`TrustUnit` validator and by `MemoryTrust.instruction_authority` being a
`Literal["none"]` on every memory row — data payloads cannot become
instructions anywhere in the store path.
