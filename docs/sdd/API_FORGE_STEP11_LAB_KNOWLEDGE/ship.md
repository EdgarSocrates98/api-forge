---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: ship
profile: critical
status: done
deviations:
  - "CVE/advisory scanning stays an unresolved external boundary — the
    audit reports it, no stub fabricates assurance"
  - "agent -> knowledge edge stays unresolved — no declared carrier
    exists in agents/*.md; the contract names it instead of inferring"
  - "5 of 13 lab scenario kinds are declared gaps (latency regression,
    auth migration, rate limit, event contract, pagination) — honest
    gaps, not fabricated coverage"
  - "dependency locking stays declared-ranges + vendored assets per
    ADR-011; uv.lock remains uncommitted setup residue"
  - "pip check is skipped inside uv venvs (no pip module); the CI job
    runs it where pip exists — reported unresolved locally"
evidence:
  - docs/sdd/API_FORGE_STEP11_LAB_KNOWLEDGE/evidence/G1-focused-tests.txt
  - docs/sdd/API_FORGE_STEP11_LAB_KNOWLEDGE/evidence/G2-evals.txt
  - docs/sdd/API_FORGE_STEP11_LAB_KNOWLEDGE/evidence/G3-gates.txt
rollback: "revert this commit; all modules, verbs, corpora, CI jobs and
  docs are additive — the freshness vocabulary extension keeps the four
  original states and the routing trust sets only grow stricter"
upstream:
  path: benchmark.md
  sha256: "989c90093009d4526a2b989e166fa3755c7ce2ab323c611d975c3df316df8e8f"
---

# ship

Phase 12 delivered: §28 lab scenario catalog with honest declared gaps;
§29 knowledge engine evolution (7-state freshness, drift rollup over
receipts, declared-edge impact graph); §30 CI parity/wheel smoke plus
deterministic supply-chain audit with the CVE boundary unresolved;
aggregate `doctor --agentic` over eight planes; and the
`SignalFreshness` widening that keeps routing semantics coherent with
the extended vocabulary.
