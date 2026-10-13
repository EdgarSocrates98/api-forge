---
sdd: 1
feature: API_FORGE_STEP11_AGENT_GOVERNOR
phase: discover
profile: critical
status: done
approaches:
  - id: supervisor-rewrite
    summary: embed governor/gain/stop/recovery inside the deterministic
      supervisor runtime and spawn agents there
    verdict: refused -- §23-§27 ask for decision primitives, not a runtime;
      embedding them in the supervisor would couple policy to execution and
      break the pure-function, side-effect-free discipline
  - id: fuzzy-gain-heuristic
    summary: treat expected information gain as a free-text intuition scored
      by a model
    verdict: refused -- gain must be a deterministic function of declared
      signals so evals, replay and policy checks can assert on it
  - id: governance-primitives
    summary: new governance/ primitives (govern, expected_gain, decide_stop,
      decide_recovery, check_loop) as pure functions over declared inputs and
      versioned policy yaml, exposed via CLI/MCP read verbs
    verdict: chosen -- additive, deterministic, honest unresolved, and leaves
      the runtime to consume decisions instead of being consumed by them
chosen: governance-primitives
---

# discover

Phase 4 of `prompt_evo_step11.md` (§23-§27): give the platform a deterministic
Agent Governor — profile/risk ceilings that clamp orchestration, expected
information gain per named action, an explicit STOP policy, governed recovery
per failure class, and repeated-strategy loop detection.

Existing pieces are reused, not rewritten: `DecisionRisk` and budget vectors
from `agentic_governance.py`, the tool-risk policy from phase 2, and the
profile vocabulary (`economy`/`balanced`/`deep`). The new surface emits
decisions; nothing in it spawns agents or spends budget.
