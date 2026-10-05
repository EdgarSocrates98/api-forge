---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: contract
profile: critical
status: draft
covers:
  - agentops-context-quality
  - agentops-decision-gates
  - agentops-model-correlation
  - runtime-governance-context
  - retrieval-provenance
  - memory-query-semantics
  - mcp-protocol-freshness
  - locked-supply-chain
upstream:
  path: intent.md
  sha256: "25b503514f2b9d03a1d176100feefa2cfc475cba4ed7ac1f14d7b7b6ca139fa5"
---

# contract

The wave is additive and fail-closed. Existing public fields remain compatible
unless a field is explicitly marked deprecated. New metrics use canonical names,
new records carry correlation identifiers, and unresolved evidence is represented
as a state rather than as zero or success.

The contract surface is documented in `docs/contracts/` and exercised by focused
tests and deterministic evidence receipts.
