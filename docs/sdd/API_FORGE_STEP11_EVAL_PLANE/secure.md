---
sdd: 1
feature: API_FORGE_STEP11_EVAL_PLANE
phase: secure
profile: critical
status: done
threat_model:
  - "adversarial corpus as real attack surface — every vector is synthetic,
    local and offline; no payload leaves the process and no fixture
    contacts a provider, host or network"
  - "memory eval setup as gate bypass — seeds enter only through
    persist_candidate, so scope/origin/evidence/trust/outcome/freshness
    gates all fire; a case that needs a forbidden scope changes the
    declared policy, not the gate"
  - "trace grading as sensitive-attribute leak — graders read the
    whitelisted AgentSpan shape; sensitive attributes are rejected by
    the existing telemetry contract before grading"
  - "rubric tampering — malformed or missing trace_rubric.yaml refuses
    AF-EVALS-TRACE-RUBRIC instead of grading with defaults"
  - "frontier fabrication — without provider-accounted cost input every
    point reports cost_state unresolved; a fixture that invents cost is
    never accepted as observed"
  - "provider tier as covert spend — the live layer ships no adapter;
    provider_status is always deferred_external and provider_results is
    empty by construction"
  - "escaped outcome normalization — an escaped synthetic attack fails
    the case; totals report escaped counts and never downgrade them"
upstream:
  path: verify.md
  sha256: "3a37e050616101e4ed1003a9b524702fdd7db87458b1bb6819dd48d5cde3c5c3"
---

# secure

The eval plane adds zero new attack surface: it executes the shipped
gates on declared corpora and records decisions. The durable threat
model — trust boundaries, injection classes, allowlist-first tool
authorization, memory gates, secret handling, containment and
rollback — lives in `docs/security/agentic-threat-model.md`.
