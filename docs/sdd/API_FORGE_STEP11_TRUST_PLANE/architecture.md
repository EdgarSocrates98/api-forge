---
sdd: 1
feature: API_FORGE_STEP11_TRUST_PLANE
phase: architecture
profile: critical
status: done
upstream:
  path: contract.md
  sha256: "6d8baf2074af0b58701f463437a6baef28e74fc24a7eaebb341232359efc73b5"
files:
  - src/apiforge/contracts/trust.py
  - src/apiforge/contracts/agentic_memory.py
  - src/apiforge/trust/plane.py
  - src/apiforge/trust/propagation.py
  - src/apiforge/trust/tools.py
  - src/apiforge/rules/tool_risk.yaml
  - src/apiforge/memory/security.py
  - src/apiforge/memory/retrieval.py
  - src/apiforge/memory/invalidation.py
  - src/apiforge/memory/store.py
  - src/apiforge/cli_agentic_state.py
  - src/apiforge/mcp/tools.py
decisions:
  - trust travels beside payloads as a TrustedRef sidecar; v1 contracts stay
    byte-identical
  - quarantine is a separate append-only log, not a flag on the record log
  - retrieval ranking reuses the query_memory filter set so both surfaces
    agree on membership and ordering
  - tool authorization ships as a control-plane primitive; runtime dispatcher
    wiring is deferred to the governor phase
---

# architecture

```text
contracts/trust.py          (frozen contracts + closed literals)
       |
       v
trust/plane.py              BASE_TRUST + ORIGIN_TAINT + REF_ORIGIN_MAP,
                            trust_unit(), annotate_ref/capsule, external_unit
trust/propagation.py        propagate(): union taint, weakest-source trust,
                            one-tier evidence lift, authority never widens
trust/tools.py              load_tool_risk(rules/tool_risk.yaml) + authorize()
                            default-deny, AF-TOOL-* codes

memory/security.py          evaluate_gates(): scope→origin→evidence→trust→
                            outcome→freshness  → persist|quarantine|reject
memory/store.py             persist_candidate() rewired onto the pipeline;
                            quarantine.jsonl (append-only); review_quarantine()
memory/retrieval.py         score_record(): 8 deterministic signals,
                            optional semantic bonus; query_memory_scored()
memory/invalidation.py      suggest_invalidations(): 8 advisory triggers
runtime/semantic_checkpoint unchanged; parity proved by test
```

`MemoryTrust` keeps `instruction_authority="none"` hard-locked on memory rows;
`TrustUnit` opens authority only for `system`/`governed_policy` origins via
validator. No new runtime dependencies; `yaml.safe_load` reads the risk policy
as data.
