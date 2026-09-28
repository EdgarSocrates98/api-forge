---
sdd: 1
feature: API_FORGE_ECONOMY_CONTEXT_GATEWAY
phase: discover
profile: standard
status: draft
approaches:
  - id: native-gateway
    summary: build ContextCapsule/ctx:// on ContextService, the case graph and the economy ledger
    verdict: chosen -- reuses existing contracts, stays hostless, offline and provider-free
  - id: forge-kernel
    summary: extract a shared Context Gateway package with Spark Forge
    verdict: refused -- premature cross-repo coupling; API graph differs from the Spark domain
  - id: measure-only
    summary: ship only RunLedger/CostVector and defer the gateway
    verdict: refused -- cannot prove reduction with equal evidence
chosen: native-gateway
---
# discover

Source: `prompt_evo_economy.md` and `.claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md`.
Existing pieces: `economy/ledger.py`, `economy/tokens.py`, `ContextService`,
`graph/impact.py`, the case graph built from `api-ir.json`/`facts.json`.
