---
sdd: 1
feature: API_FORGE_STEP11_AGENT_GOVERNOR
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/agentic_governance.py
  - src/apiforge/governance/governor.py
  - src/apiforge/governance/gain.py
  - src/apiforge/governance/stop.py
  - src/apiforge/governance/recovery.py
  - src/apiforge/governance/loop.py
  - src/apiforge/rules/governor_policy.yaml
  - src/apiforge/rules/recovery_policy.yaml
  - src/apiforge/cli_governor.py
  - src/apiforge/cli.py
  - src/apiforge/mcp/tools.py
  - src/apiforge/evals/agent_governor.py
  - evals/corpus/agent-governor/
  - tests/contracts/test_agentic_governor.py
  - tests/governance/
  - docs/contracts/
decisions:
  - "primitives are pure functions; side effects belong to the phase-5 control
    plane that consumes GovernorDecision"
  - "the failure-class vocabulary is closed: undeclared classes refuse
    AF-GOV-FAILURE-CLASS-UNKNOWN instead of being coerced"
  - "absent signals land in unresolved and are dropped from the gain mean —
    never counted as zero"
  - "an unmeasurable gain fails closed: STOP with AF-GOV-GAIN-UNRESOLVED"
  - MCP exposes read-only projections (decide/stop/recover); no write verb
upstream:
  path: contract.md
  sha256: "acc28a50435235bbfefe119bbcfb4f99dbc40260311c15ffc14b2d743741a8ff"
---

# architecture
