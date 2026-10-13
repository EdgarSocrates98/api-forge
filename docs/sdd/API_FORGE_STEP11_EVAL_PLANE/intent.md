---
sdd: 1
feature: API_FORGE_STEP11_EVAL_PLANE
phase: intent
profile: critical
status: done
risk_class: medium
problem: the agentic platform can replay quality but cannot grade recorded
  traces, prove containment against injection classes, exercise the eight
  memory eval axes through real gates, compare profiles on a
  quality/cost/latency frontier, or report an honest live-eval layer —
  every gap currently resolves to "no signal" instead of explicit
  unresolved states
success: "evals trace-grading grades AgentSpan traces per rubric
  dimension and returns unresolved for empty/mixed traces; evals
  security-adversarial runs the synthetic offline corpus and reports
  contained/refused/escaped with zero escapes; evals memory-evals covers
  usefulness/poisoning/stale/wrong-env/conflict/leakage/retrieval/
  invalidation through persist_candidate; evals frontier compares
  economy/balanced/deep with cost unresolved without provider data;
  evals live reports the deterministic tier plus provider_tier
  deferred_external; docs/security/agentic-threat-model.md documents
  the threat classes and controls"
out_of_scope:
  - live provider adapters or any network/model call (human-gated
    external boundary, deferred_external by design)
  - mutating governed runtime, memory or trust code — evals exercise
    the existing gates, they do not rewrite them
  - claiming observed provider cost or latency (unresolved unless
    provider-accounted input files are supplied)
  - attack payloads beyond the synthetic offline corpus
upstream:
  path: discover.md
  sha256: "887319e9e35fd8d7c5582c99949849e1cf6afbb8220691587d517160640b37e2"
---

# intent

An eval plane over the existing gates, never a bypass around them.
Memory seeds flow through `persist_candidate`; adversarial inputs flow
through the real trust/tool/memory gates; frontier costs stay
unresolved without provider-accounted data; the live layer names its
deferred provider boundary instead of fabricating results.
