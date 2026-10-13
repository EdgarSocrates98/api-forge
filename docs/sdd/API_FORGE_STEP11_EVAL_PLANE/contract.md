---
sdd: 1
feature: API_FORGE_STEP11_EVAL_PLANE
phase: contract
profile: critical
status: done
covers:
  - trace-grading
  - rubric-policy
  - live-eval-layer
  - provider-deferral
  - quality-frontier
  - adversarial-corpus
  - memory-evals
  - unresolved-honesty
  - cli-surface
  - eval-corpus
contracts:
  - TraceGradeDimension/v1
  - TraceGrade/v1
  - TraceGradingReport/v1
  - LiveEvalLayer/v1
  - LiveEvalReport/v1
  - FrontierPoint/v1
  - QualityFrontier/v1
  - AdversarialCaseResult/v1
  - SecurityAdversarialReport/v1
  - MemoryEvalCaseResult/v1
  - MemoryEvalReport/v1
refusals:
  - AF-EVALS-TRACE-RUBRIC -- malformed or missing trace rubric policy
  - AF-EVALS-TRACE-SPAN -- span record fails AgentSpan validation
  - AF-EVALS-LIVE-LAYER -- malformed or missing live-eval layer policy
  - AF-EVALS-FRONTIER -- frontier input report fails contract validation
  - AF-EVALS-INPUT-INVALID -- corpus case fails declared schema
invariants:
  - empty, mixed-trace or insufficient traces grade to unresolved, never
    to an invented score
  - aggregate scores cover observed dimensions only; estimated and
    unresolved dimensions are never folded in silently
  - security outcomes are exactly contained|refused|escaped; an escaped
    synthetic attack is a failed case, not a warning
  - memory eval setup flows through persist_candidate; no corpus row
    bypasses scope/origin/evidence/trust/outcome/freshness gates
  - cost and provider metrics stay unresolved without provider-accounted
    input; zero is never substituted for unknown
  - no provider SDK import and no network call anywhere in the plane
upstream:
  path: intent.md
  sha256: "8e7023b190082fdd3f0af770bba39fda55173dad29e40588cffa5235d7d57ca2"
---

# contract

Eleven contracts under `eval_plane.py`, all `VersionedContract`:
per-dimension grades with evidence refs and unresolved lists, reports
with per-case results, the live-eval layer descriptor that names its
declared evals/profiles/metrics and its deferred provider tier, frontier
points with `cost_state`, and adversarial/memory case results that
record the observed gate path.
