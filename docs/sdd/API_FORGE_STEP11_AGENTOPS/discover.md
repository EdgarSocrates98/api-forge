---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: discover
profile: critical
status: done
approaches:
  - id: provider-backed-observability
    summary: ship AgentOps data to a hosted observability product
    verdict: refused -- the platform is offline-first; a provider call
      would break determinism and leak run payloads
  - id: invent-metrics
    summary: synthesize quality/cost numbers when ledgers are silent
    verdict: refused -- §57 forbids fabricated claims; absence must be
      named unresolved
  - id: local-ledger-projection
    summary: join run ledger + token ledger + span store + context-quality
      derivation + memory store + decision gates into one sectioned report,
      a deterministic axis comparison and a declared-policy waste detector
    verdict: chosen -- additive, offline, honest about missing sources
chosen: local-ledger-projection
---

# discover

§53–§57 asks for `agentops inspect`, `agentops compare` and a token-waste
detector. All source ledgers already exist locally; nothing new is needed
beyond deterministic joins and a declared detector policy.
