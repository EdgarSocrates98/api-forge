# CapabilityRecord/v1

`CapabilityRecord` is the public support declaration for one API Forge
operation. It records the state (`supported`, `heuristic`, `unresolved` or
`unsupported`), vertical, operation, surfaces, evidence, limitations,
prerequisites, risk, rollback, documentation and verifier.

The record is declarative. It does not grant permission to execute an external
action. A supported record means only that the named scope has a reproducible
verifier and declared evidence boundary.
