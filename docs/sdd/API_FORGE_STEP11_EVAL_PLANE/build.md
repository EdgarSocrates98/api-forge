---
sdd: 1
feature: API_FORGE_STEP11_EVAL_PLANE
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: 11 contracts + registry + exports + AF-EVALS-* catalog codes + contract docs + rubric/layer policies
    files: [src/apiforge/contracts/eval_plane.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, src/apiforge/rules/trace_rubric.yaml, src/apiforge/rules/live_evals.yaml, docs/contracts/, docs/catalog-contract.md]
  - id: B2
    summary: trace grading over AgentSpan with dimension scoring, observed-only aggregation and unresolved honesty
    files: [src/apiforge/evals/trace_grading.py, evals/corpus/trace-grading/]
  - id: B3
    summary: synthetic adversarial corpus over trust/tool/memory gates with contained|refused|escaped outcomes
    files: [src/apiforge/evals/security_adversarial.py, evals/corpus/security-adversarial/]
  - id: B4
    summary: memory evals over persist_candidate/retrieval/invalidation covering the eight §24 axes
    files: [src/apiforge/evals/memory_evals.py, evals/corpus/memory-evals/]
  - id: B5
    summary: live-eval layer (deferred_external) + quality/cost/latency frontier + CLI verbs + tests + threat model
    files: [src/apiforge/evals/live_evals.py, src/apiforge/evals/frontier.py, src/apiforge/cli.py, tests/evals/test_eval_plane.py, docs/security/agentic-threat-model.md]
claims:
  - "trace grading scores each rubric dimension independently and aggregates observed dimensions only; empty or multi-trace inputs return unresolved"
  - "the adversarial corpus reports 9/9: 3 contained and 6 refused, 0 escaped — no synthetic attack becomes trusted instruction"
  - "memory evals report 9/9 across usefulness, poisoning, stale, wrong-environment, conflict, leakage, retrieval and invalidation axes"
  - "the frontier computes pareto by constructing replacement points; cost_state stays unresolved for all profiles without provider-accounted input"
  - "evals live reports the deterministic tier (4 evals, 0 failed) and provider_tier deferred_external with an explicit unresolved notice"
upstream:
  path: plan.md
  sha256: "f72806e6df05ffb732b4e69155db196d31ca662acfd4477a11ba85940709dfea"
---

# build

All modules are additive. No governed runtime, memory, trust or MCP
code was rewritten; the eval plane consumes the shipped gates and
records what they decide.
