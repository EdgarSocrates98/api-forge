---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: intent
profile: critical
status: done
risk_class: medium
problem: the platform ships knowledge packs that cannot express
  deprecation, conflict or verified freshness; no declared relation
  graph exists between sources, packs, rules, skills, agents and evals;
  the lab matrix has no scenario contract separating real coverage from
  gaps; doctor inspects the economy plane only; CI validates one
  interpreter on one OS and never installs the built wheel; and no
  deterministic supply-chain audit exists — each gap resolves to "no
  signal" instead of explicit unresolved states
success: "lab scenarios emits all 13 §28 scenario kinds with covered
  cells pointing to real fixtures/evals/proofs and declared-gap cells
  naming what is missing; knowledge drift rolls receipts into
  verified/stale/conflicted/deprecated/unresolved with conflict pairs
  named; knowledge impact emits the declared source->pack->rule->
  skill->eval graph with agent->knowledge unresolved; doctor --agentic
  reports eight planes with findings, unlocks and unresolved; CI runs
  windows parity + wheel smoke + supply-chain audit; evals
  knowledge-drift passes 5/5"
out_of_scope:
  - live CVE/advisory scanning (external database boundary — reported
    unresolved, never faked)
  - agent -> knowledge edge inference (no declared carrier exists —
    stays unresolved)
  - lockfile adoption (ADR-011 records declared-ranges choice)
  - generated lab fixtures for gap cells
  - any provider or network call from the new modules
upstream:
  path: discover.md
  sha256: "90d4dfa7b99a63f01ba473bead1d5547dc57232c0839c9a9d11b5ef9d44383ed"
---

# intent

Phase 12 delivers §28 (API Forge Lab), §29 (Knowledge Engine
Evolution), §30 (CI and Supply Chain) and the aggregate
`doctor --agentic`. The work is additive: existing Pack metadata,
freshness receipts, the economy doctor checks and the CI workflow are
reused, not rewritten.
