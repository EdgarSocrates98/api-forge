---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: discover
profile: critical
status: done
approaches:
  - id: infer-agent-knowledge-edges
    summary: derive agent -> pack edges from tool names, skill text or
      heuristic matching when no declared relation exists
    verdict: refused -- the roadmap requires a declared relation
      contract; inferred edges fabricate provenance and poison the
      impact graph consumers rely on for blast-radius questions
  - id: lab-as-generated-fixtures
    summary: auto-generate fixture apps per technology x case cell so
      the lab matrix reports full coverage
    verdict: refused -- a generated cell without a real fixture, eval or
      proof would claim coverage that does not exist; §28 requires
      honest declared gaps, and fabricated fixtures are worse than a
      named gap
  - id: lockfile-adoption
    summary: adopt uv.lock/poetry.lock as the dependency strategy now
    verdict: refused -- the declared-range + vendored-assets strategy is
      deliberate and verified; ADR-011 records the decision and its
      revisit trigger instead of changing strategy mid-phase
  - id: cve-scan-offline-stub
    summary: ship a stub that always reports "no vulnerabilities" so the
      supply-chain audit reports clean
    verdict: refused -- CVE scanning needs an external advisory
      database; an offline stub fabricates assurance. The audit reports
      the boundary as unresolved
  - id: declared-lab-knowledge-ci
    summary: scenario catalog with covered cells pointing to real
      fixtures/evals and explicit declared gaps; knowledge drift over
      read-only receipts; declared-edge impact graph; cross-plane
      agentic doctor; CI parity + wheel smoke + deterministic
      supply-chain audit
    verdict: chosen -- additive, offline-first, reuses Pack metadata,
      source_authority receipts, the economy doctor shape and existing
      CI; every unknown stays unresolved
chosen: declared-lab-knowledge-ci
---

# discover

§28–§30 close the platform loop: the lab proves scenarios instead of
claiming them, knowledge packs can drift and must report it, CI must
validate the artifact users actually install, and the platform must
diagnose its own agentic health across planes. The existing substrate is
solid — `tests/labs` matrix, `knowledge/freshness.py` with a four-state
vocabulary, an economy-only doctor, a single-python CI job and a vendor
manifest check. What is missing is the scenario contract that separates
coverage from declared gaps, the drift rollup over observation
receipts, the declared-edge knowledge impact graph, the aggregate
doctor, and the CI/supply-chain wave.
