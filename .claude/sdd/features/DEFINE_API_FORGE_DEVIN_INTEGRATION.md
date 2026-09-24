# Define: API Forge Devin Desktop / CLI / Cloud integration

Status: ✅ Complete (Built)

## User outcome

An operator can generate an auditable `DevinPayload/v1` for a planning,
implementation, verification, review or handoff task and use the same API
Forge operating contract from Devin Desktop, CLI or Cloud.

## Acceptance criteria

- [x] Closed Pydantic contracts with evidence level and limitations.
- [x] `apiforge devin payload`, `probe` and `capabilities` commands.
- [x] CLI probe is local and read-only.
- [x] `.devin/` config, hooks, skill, reviewer and MCP example.
- [x] Destructive-command hook emits `AF-DEVIN-DESTRUCTIVE-COMMAND`.
- [x] Native Windows sandbox request emits `AF-DEVIN-SANDBOX-UNAVAILABLE`.
- [x] Official Desktop/CLI/Cloud behavior is documented with unresolved
  account/organization/runtime boundaries.
- [x] Focused tests, Ruff and mypy pass.

## Required handoff

Status, Outcome, Human action, Proof, Gaps, Next and Open remain mandatory.
