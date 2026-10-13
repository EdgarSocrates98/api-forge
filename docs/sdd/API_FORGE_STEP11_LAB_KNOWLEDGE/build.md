---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: FreshnessState extended (+verified/conflicted/deprecated), PackApplicability + PackFreshness.last_validated/applies_to, KnowledgeDrift + KnowledgeImpactReport contracts, NodeKind += knowledge|skill|source, SignalFreshness widened to the canonical literal, registry + exports + 7 contract docs + AF-* catalog
    files: [src/apiforge/contracts/knowledge.py, src/apiforge/contracts/graph.py, src/apiforge/contracts/routing.py, src/apiforge/contracts/scorecard_routing.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, docs/contracts/, docs/catalog-contract.md]
  - id: B2
    summary: knowledge/drift.py receipt rollup + knowledge/impact.py declared-edge graph + freshness.py evolution + evals knowledge-drift + 5-case corpus
    files: [src/apiforge/knowledge/drift.py, src/apiforge/knowledge/impact.py, src/apiforge/knowledge/freshness.py, src/apiforge/evals/knowledge_drift.py, evals/corpus/knowledge-drift/]
  - id: B3
    summary: lab catalog (scenarios.yaml + loader) + lab scenarios verb + scenario tests — 13 kinds, 8 covered, 5 declared gaps
    files: [src/apiforge/labs/catalog.py, src/apiforge/labs/scenarios.yaml, tests/labs/test_scenarios.py]
  - id: B4
    summary: agentic doctor — AgenticDoctorReport over 8 planes + doctor --agentic + tests
    files: [src/apiforge/contracts/agentic_health.py, src/apiforge/runtime/agentic_doctor.py, tests/runtime/test_agentic_doctor.py]
  - id: B5
    summary: CLI verbs (knowledge drift|impact, lab scenarios, doctor --agentic, evals knowledge-drift) + 3 read-only MCP tools + routing trust-set updates
    files: [src/apiforge/cli.py, src/apiforge/mcp/tools.py, src/apiforge/runtime/routing.py, src/apiforge/runtime/model_router.py]
  - id: B6
    summary: supply-chain audit script + CI windows-parity + wheel-smoke jobs + 14 corpus READMEs + ADR-011
    files: [scripts/supply_chain_audit.py, .github/workflows/ci.yml, evals/corpus/, docs/decisions/ADR-011-dependency-locking.md]
claims:
  - "lab scenarios reports 13 declared kinds: 8 covered via real fixture/eval/proof pointers, 5 honest declared gaps, 0 unresolved cells"
  - "knowledge drift: 5/5 eval cases (verified, stale, conflicted, deprecated, unresolved); conflicts name the disagreeing pairs"
  - "knowledge impact: 40 packs, 342 nodes, 454 edges from declared data only; agent->knowledge edge named unresolved"
  - "doctor --agentic composes 8 plane sections; unobservable planes report unresolved, never an implied pass"
  - "supply-chain audit: dependency inventory + pip check + vendor parity + corpus consistency (29 corpora, 195 cases) + surface_lock on the full 151-tool MCP surface; CVE scanning reported unresolved"
upstream:
  path: plan.md
  sha256: "93f4f5e8dd78732eb60767fa17d99481a5d103d1bede75292527376acb87c849"
---

# build

Implemented §28–§30 plus the aggregate agentic doctor. All modules are
deterministic and offline; no provider SDK, network call or silent
mutation was added. The `SignalFreshness` widening flowed through the
routing trust sets so `verified` counts as trusted and
`conflicted`/`deprecated` as untrusted — the champion lane accepts
`{"fresh", "verified"}`.
