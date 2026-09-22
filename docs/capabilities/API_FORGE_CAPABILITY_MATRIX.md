# API Forge Capability Matrix

The machine-readable source is
`src/apiforge/rules/capability_matrix.yaml`. This document explains how to
read it and what the states mean.

For an end-to-end operator workflow, see
[API Forge Platform Usage](../guides/API_FORGE_PLATFORM_USAGE.md).

| State | Meaning | What it does not mean |
|-------|---------|-----------------------|
| `supported` | The local path has a contract, evidence source and verifier | It does not prove every provider or runtime mode |
| `heuristic` | A deterministic projection can provide useful guidance from static or declared evidence | It does not prove live behavior, indexes, lag, cost or performance |
| `unresolved` | The question is valid, but required evidence or a safe adapter is missing | It is not a negative finding |
| `unsupported` | The current product boundary intentionally refuses the capability | It is not silently attempted |

Every public record declares its vertical, operation, supported surfaces,
evidence, limitations, prerequisites, risk, rollback and verifier. The command
`apiforge capabilities verify` checks those fields and documentation paths.

## Core capabilities

| Capability | State | Verifier | Main limitation |
|------------|-------|-----------|-----------------|
| `api.analyze` | supported | `tests/e2e/test_platform_completion.py::test_platform_chain` | Static adapters do not execute application code. |
| `api.next-step` | supported | `tests/e2e/test_next_step.py` | Findings must map to the routing catalog. |
| `api.provenance` | supported | `tests/e2e/test_platform_completion.py::test_platform_chain` | Acceptance still requires independent verification. |
| `database.inspect` | heuristic | `tests/labs/test_platform_verticals.py::test_vertical_coverage` | Query plans, indexes and cardinality require database evidence. |
| `messaging.inspect` | heuristic | `tests/labs/test_platform_verticals.py::test_vertical_coverage` | Broker lag and delivery guarantees require observations. |
| `cicd.inspect` | heuristic | `tests/labs/test_platform_verticals.py::test_vertical_coverage` | Pipeline configuration does not prove execution. |
| `cloud.inspect` | heuristic | `tests/labs/test_platform_verticals.py::test_vertical_coverage` | Remote state and live posture require explicit evidence. |
| `frontend.inspect` | heuristic | `tests/labs/test_platform_verticals.py::test_vertical_coverage` | Browser behavior and accessibility need a frontend host. |
| `git.plan` | unresolved | `tests/runtime/test_supervisor.py` | The offline core does not mutate a Git host. |
| `external.apply` | unsupported | `tests/runtime/test_supervisor.py` | Live mutation requires an approved provider adapter and rollback. |

## Evidence rules

- A fixture is an input example, not production proof.
- A golden is a reviewed expected result for a representative input.
- A holdout exercises uncertainty, missing evidence or a negative path.
- A receipt binds persisted artifacts to hashes and policy metadata.
- An agent recommendation must separate facts, assumptions, risks and
  unresolved items.
- Missing external tooling remains visible as a prerequisite or limitation.

## Adding a capability

Add a record to the YAML matrix, document it here, add a verifier and provide
the corresponding fixture, golden and holdout when it belongs to a required
vertical. Do not change `unsupported` to `supported` because a parser or a
prompt exists; the state change requires independent evidence.
