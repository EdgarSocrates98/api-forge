---
sdd: 1
feature: API_FORGE_AGENTIC_PLATFORM
phase: contract
profile: critical
status: ready
upstream:
  path: intent.md
  sha256: "709f022125e4728e4d5a25bc0314352157e9dea10d3fea6b4375ffcfe8d89d13"
covers:
  - ArtifactRef/v1, Fact/v1, Finding/v1, Receipt/v1 (existing models gain version)
  - Decision/v1, ActionPlan/v1, Verification/v1
  - TaskSpec/v1, TaskRevision/v1, TaskPlan/v1, TaskHandoff/v1
  - AcceptanceRecord/v1, CapabilityProof/v1, OutcomeBrief/v1
  - GraphNode/v1, GraphEdge/v1
  - TelemetryEvent/v1, PerformanceRun/v1, DataAccessIR/v1, RuntimeMatrix/v1 (stubs)
api_ir: docs/specs/2026-09-21-api-forge-design.md
---

# contract

Every canonical contract carries: `version`, stable `id`, `provenance`,
`sha256`-addressed content where meaningful, `produced_by`, `status`, and an
`unresolved`/`refused` surface. Contracts are closed (`extra="forbid"`),
frozen, and covered by `tests/contracts/test_<name>.py` conformance tests
(golden round-trip, required fields, closed schema).

## Delivered in full now

- `TaskSpec/v1`: outcome, size, writable_paths, inputs, dependencies,
  preconditions, tests, expected_proofs, budgets (calls, rounds, deadline),
  risk, strategy, rollback, acceptance_criteria, capability_covered.
- `TaskRevision/v1`: revision number, changed fields, `sealed_by` +
  `seal_signature_b64` + `public_key_sha256` (Ed25519 -- existing
  `report/keys.py`); any change invalidates the seal.
- `TaskPlan/v1` + `TaskHandoff/v1`: recipe step sequence and the
  executor handoff record.
- `AcceptanceRecord/v1`: `accepted_by` distinct from `executed_by` by
  construction.
- `CapabilityProof/v1`: which capability a test/bench proves.
- `OutcomeBrief/v1`: status in {DONE, REVIEW, DECIDE, BLOCKED, FAILED};
  DONE refused by the brief validator when mandatory gaps exist.
- `Decision/v1`, `ActionPlan/v1`, `Verification/v1`.
- `GraphNode/v1`, `GraphEdge/v1`: `id`, `kind`, `props`, `sha256`; edge
  kinds are the closed list from the prompt.
- Existing `Fact`, `Finding`, `Receipt` gain `version: Literal[1] = 1`.

## Stub contracts (shape lands with their layer)

`TelemetryEvent/v1`, `PerformanceRun/v1`, `DataAccessIR/v1`,
`RuntimeMatrix/v1` -- version + identity + provenance + unresolved surface
only. Declared as stubs so consumers bind to a real contract early.

## CLI surface added

`contract list`, `contract show <name>` (JSON schema), `task create/review/
seal/run/accept/reject/park/status`, `brief show`, `graph build/query/
impact/trace/coverage/export`, `index build/status`, cache via extractors.
