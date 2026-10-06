---
sdd: 1
feature: API_FORGE_ECONOMY_CONTEXT_GATEWAY
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "3ccee0c342ea91da545f4969d607756b5a7d6e57cf5f181ce8561225cf430d8b"
covers: [ContextRef/v1, ContextCapsule/v1, CapsuleBudget/v1, CapsuleRefusal/v1, CostVector/v1, LedgerRef/v1, RunLedgerEntry/v1]
api_ir:
  input: target operation, case directory, byte budget, max level L0-L4, impact mode
  output: capsule with ctx://sha256 refs, budget, refusals, unresolved and status
---
# contract

Contracts are frozen and closed. `ctx://sha256/<hex>` is identity; kind,
label, source and span are metadata. `observed_tokens` defaults to null —
bytes are never converted into tokens.
