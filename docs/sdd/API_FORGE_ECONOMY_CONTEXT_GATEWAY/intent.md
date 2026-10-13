---
sdd: 1
feature: API_FORGE_ECONOMY_CONTEXT_GATEWAY
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "e2766b45cd182ab0818aa712d54bd2e6879cfd9a15e3bd90740780fff7acec05"
problem: >
  Agent hosts and hostless operators receive raw, redundant context and the
  economy ledger cannot say which source spent the bytes, so no reduction can
  be proven without an evidence regression.
success: [capsule-ctx-refs, hash-verified-expand, attributed-ledger, economy-eval-gate, catalog-codes]
out_of_scope: [shared-user-cache, incremental-graph, budget-envelope, economy-profiles, runtime-routing-integration, llm-summarization]
owner: api-forge-economy
---
# intent

Deliver the minimum sufficient evidence for one operation, measured and
attributable, with quality as a floor and tokens only when observed.
