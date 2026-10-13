---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: contract
profile: critical
status: done
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
  sha256: "cbb3f52652165d177b74a66d31600d5ea049f5dae6d4fba001e2f7a2adfed309"
---

# contract

The wave is additive and fail-closed. Existing public fields remain compatible
unless a field is explicitly marked deprecated. New metrics use canonical names,
new records carry correlation identifiers, and unresolved evidence is represented
as a state rather than as zero or success.

The contract surface is documented in `docs/contracts/` and exercised by focused
tests and deterministic evidence receipts.
