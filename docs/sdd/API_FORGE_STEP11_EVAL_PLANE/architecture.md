---
sdd: 1
feature: API_FORGE_STEP11_EVAL_PLANE
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/eval_plane.py
  - src/apiforge/contracts/registry.py
  - src/apiforge/contracts/__init__.py
  - src/apiforge/evals/trace_grading.py
  - src/apiforge/evals/security_adversarial.py
  - src/apiforge/evals/memory_evals.py
  - src/apiforge/evals/live_evals.py
  - src/apiforge/evals/frontier.py
  - src/apiforge/rules/trace_rubric.yaml
  - src/apiforge/rules/live_evals.yaml
  - src/apiforge/cli.py
  - evals/corpus/trace-grading/
  - evals/corpus/security-adversarial/
  - evals/corpus/memory-evals/
  - evals/corpus/frontier/
  - tests/evals/test_eval_plane.py
  - docs/security/agentic-threat-model.md
  - docs/contracts/ (11 eval-plane docs)
  - docs/catalog-contract.md
decisions:
  - "frontier consumes the agentic-quality report instead of re-measuring
    quality — one measured source keeps floors, baselines and regression
    analysis consistent"
  - "rubric dimensions, signals and thresholds live in
    rules/trace_rubric.yaml — policy is declared data, never hidden in
    a detector"
  - "adversarial and memory corpora exercise the shipped trust/tool/
    memory gates — seeds enter through persist_candidate only"
  - "the live layer is a declared descriptor plus deferred_external
    status, not a stub adapter — a fake adapter would fabricate
    capability"
  - "pareto flags are applied by constructing replacement FrontierPoint
    instances — contract immutability is a platform invariant"
upstream:
  path: contract.md
  sha256: "ef33f5e841585d6d96b4a8b2bb36563558afee96b7a8b090cdbdeb14fc12f5ed"
---

# architecture

```text
deterministic tier (CI gate)
  agentic-quality | trace-grading | security-adversarial | memory-evals
        |                |               |                    |
   recorded outputs   AgentSpan      trust/tool gates    memory gates
                       rubric        (synthetic only)    persist_candidate
        \________________\_____________|____________________/
                          v
                 evals live (LiveEvalReport)
                 provider_tier: deferred_external
                          v
                 evals frontier (QualityFrontier)
                 quality x latency x cost; pareto by replacement
```

Every tier is offline; the provider tier is a declared boundary, not
code that runs inside the core.
