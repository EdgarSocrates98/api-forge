---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: plan
profile: critical
status: done
tasks:
  - id: G1
    covers: [freshness-vocabulary, pack-applicability, knowledge-drift, knowledge-impact-graph, lab-scenario-catalog, agentic-doctor]
    test: sdd/API_FORGE_STEP11_LAB_KNOWLEDGE/evidence/G1-focused-tests.txt
  - id: G2
    covers: [knowledge-drift, lab-scenario-catalog, agentic-doctor, supply-chain-audit, unresolved-honesty]
    test: sdd/API_FORGE_STEP11_LAB_KNOWLEDGE/evidence/G2-evals.txt
  - id: G3
    covers: [freshness-vocabulary, ci-parity-wheel, refusal-codes]
    test: sdd/API_FORGE_STEP11_LAB_KNOWLEDGE/evidence/G3-gates.txt
upstream:
  path: architecture.md
  sha256: "0911202a29e741a8b678016a8a8b89b301fc2d26b9e07a789f1827f99ce30d21"
---

# plan

G1 — focused pytest: knowledge evolution (drift states, receipt
disagreement, deprecated, applicability), lab catalog validation,
agentic doctor sections, MCP surface parity — 26 passed.

G2 — deterministic evals and smokes: `evals knowledge-drift` 5/5;
`lab scenarios` 13 scenarios (8 covered, 5 declared gaps);
`doctor --agentic` cross-plane report; `knowledge impact` graph;
`mcp audit` 0 findings on 151 tools; `supply_chain_audit.py` with the
CVE boundary unresolved.

G3 — static gates: Ruff check + format over the changed surface and
mypy over `src/apiforge` (the CI gate), all clean after widening
`SignalFreshness` to the canonical `FreshnessState`.
