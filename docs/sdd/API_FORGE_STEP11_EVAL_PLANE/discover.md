---
sdd: 1
feature: API_FORGE_STEP11_EVAL_PLANE
phase: discover
profile: critical
status: done
approaches:
  - id: new-quality-runner
    summary: build a second quality runner alongside agentic-quality to
      host live/provider calls
    verdict: refused -- §23 asks for a layered architecture, not a
      duplicate runner; agentic_quality already replays recorded outputs
      per profile with floors and baselines
  - id: inline-provider-tier
    summary: let eval commands call provider adapters directly when an
      API key is present in the environment
    verdict: refused -- provider calls are a human-gated external
      boundary; the core must never silently spend money or leak
      prompts; tier must report deferred_external
  - id: eval-plane-layered
    summary: keep deterministic corpora as the CI gate, add rubric-driven
      trace grading, synthetic adversarial and memory corpora, a
      quality/cost/latency frontier and an honest live-eval layer
    verdict: chosen -- additive, offline-first, reuses AgentSpan,
      memory gates, trust tools and the recorded-quality runner;
      every unresolved state stays explicit
chosen: eval-plane-layered
---

# discover

§23–§25 and the trace/frontier requirements ask for the eval plane that
closes the agentic loop: deterministic eval → live model eval → trace
grading → profile comparison → regression analysis. The platform already
replays recorded agentic outputs (agentic_quality), records AgentSpan
traces, enforces memory gates and authorizes tools through declared
policy. What is missing is the rubric that turns traces into graded
evidence, the synthetic adversarial corpus that exercises containment,
the memory corpus over the real persistence gates, the profile frontier
and the honest live-eval layer that never calls a provider by itself.
