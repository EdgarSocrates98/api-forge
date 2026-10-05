---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/knowledge.py
  - src/apiforge/contracts/agentic_health.py
  - src/apiforge/contracts/lab.py
  - src/apiforge/contracts/graph.py
  - src/apiforge/contracts/routing.py
  - src/apiforge/contracts/scorecard_routing.py
  - src/apiforge/contracts/registry.py
  - src/apiforge/contracts/__init__.py
  - src/apiforge/knowledge/freshness.py
  - src/apiforge/knowledge/drift.py
  - src/apiforge/knowledge/impact.py
  - src/apiforge/runtime/agentic_doctor.py
  - src/apiforge/runtime/routing.py
  - src/apiforge/runtime/model_router.py
  - src/apiforge/labs/catalog.py
  - src/apiforge/labs/scenarios.yaml
  - src/apiforge/evals/knowledge_drift.py
  - src/apiforge/cli.py
  - src/apiforge/mcp/tools.py
  - scripts/supply_chain_audit.py
  - .github/workflows/ci.yml
  - evals/corpus/knowledge-drift/
  - evals/corpus/ (14 READMEs added)
  - tests/knowledge/test_evolution.py
  - tests/labs/test_scenarios.py
  - tests/runtime/test_agentic_doctor.py
  - tests/mcp/test_tools.py
  - docs/contracts/ (7 contract docs)
  - docs/decisions/ADR-011-dependency-locking.md
  - docs/catalog-contract.md
decisions:
  - "drift consumes explicit SourceObservation receipts only — the module
    never fetches a source, so freshness stays a deterministic function
    of declared inputs"
  - "conflicted reports the disagreeing receipt pairs instead of
    averaging — a disagreement is evidence, not noise"
  - "the impact graph derives edges from declared data only
    (pack.yaml, source_authority, evals.yaml, rule catalog, skill
    manifests); agent->knowledge stays unresolved because no agent
    manifest declares a pack relation"
  - "SignalFreshness is widened to the canonical FreshnessState instead
    of mapping extended states down — verified is strictly stronger
    than fresh and conflicted/deprecated join the untrusted set"
  - "the agentic doctor composes per-plane sections and never mutates —
    unobservable planes report unresolved instead of an implied pass"
  - "the supply-chain audit reports the CVE boundary as unresolved and
    locks the full MCP surface via full_tools(), not the base tuple"
upstream:
  path: contract.md
  sha256: "b6725f94dc18a5a68b683bad425673d8630446873fb4e4d6840d03a019ffcd7a"
---

# architecture

```text
pack.yaml + source_authority.yaml (declared)
  -> freshness.py (4-state)  --extended-->  FreshnessState (7-state)
  -> drift.py: receipts -> KnowledgeDrift (verified|stale|conflicted|
     deprecated|unresolved, conflict pairs named)
  -> impact.py: declared edges -> KnowledgeImpactReport
     (source->pack->rule->skill->eval; agent->knowledge unresolved)

labs/scenarios.yaml -> labs/catalog.py -> LabReport
  (13 kinds; covered = fixture|eval|proof, else declared-gap;
   AF-LAB-CELL-* on both/neither)

runtime/agentic_doctor.py -> AgenticDoctorReport
  sections: case, memory(+quarantine), trust(policy), telemetry(spans),
  evals(corpus), sdd(chain), mcp(registry), economy(existing checks)

scripts/supply_chain_audit.py -> dependency inventory, pip check,
  vendor parity, corpus consistency, surface_lock (151 tools);
  CVE scan -> unresolved (external boundary)

ci.yml: +supply-chain step, +windows-parity job, +wheel-smoke job
```
