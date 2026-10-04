---
sdd: 1
feature: API_FORGE_STEP11_CONTROL_PLANE
phase: discover
profile: critical
status: done
approaches:
  - id: replace-decision-gate
    summary: fold the lifecycle into governance/decision.py, replacing the
      fail-closed gate with mode-aware admission
    verdict: refused -- §28 mandates the existing gate stays; lifecycle is an
      orthogonal route-level concern, not a per-request admission rule
  - id: global-mode-flag
    summary: one global mode flag for the whole platform
    verdict: refused -- §29-§32 scope modes per route; a global flag could not
      promote model_routing while tool_authorization stays in shadow
  - id: declared-routes-overlay
    summary: routes declared in yaml with an append-only modes.jsonl state
      overlay, shadow records in their own ledger, promotion gated by the
      five §31 requirements plus an approved ApprovalGate
    verdict: chosen -- declarative, auditable, one-step transitions, safe
      demotion always allowed
chosen: declared-routes-overlay
---

# discover

Phase 5 of `prompt_evo_step11.md` (§28-§32): the existing fail-closed
Decision Gate stays; add a route-level lifecycle where a new decision system
runs in shadow (parallel, never governing), recommends in assisted, governs
in active only after promotion gates, and falls back to a declared route on
degradation triggers.
