---
sdd: 1
feature: API_FORGE_STEP11_CONTROL_PLANE
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/agentic_governance.py
  - src/apiforge/governance/control_plane.py
  - src/apiforge/rules/control_plane.yaml
  - src/apiforge/cli_control.py
  - src/apiforge/cli.py
  - src/apiforge/mcp/tools.py
  - src/apiforge/evals/control_plane.py
  - evals/corpus/control-plane/
  - tests/governance/test_control_plane.py
  - tests/mcp/test_tools.py
  - docs/contracts/
decisions:
  - "route state lives in an append-only modes.jsonl overlay; the declared
    yaml is never mutated and the latest row wins"
  - "shadow evaluation both records a ShadowRecord and returns legacy as
    governing — observation and authority stay separate"
  - "promotion moves exactly one step; a skipped stage or an active→active
    request refuses AF-GOV-MODE-TRANSITION-INVALID"
  - "terminal routes declare no fallback_route; degradation on one refuses
    AF-GOV-FALLBACK-MISSING rather than recursing"
  - MCP exposes read-only projections (routes/shadow/triggers); eval,
    promote and demote stay CLI write verbs
upstream:
  path: contract.md
  sha256: "3a85a6e78e3b9ed15b79ac101f6ac9c895b8683153cdaeeb36bd9227825f995e"
---

# architecture
