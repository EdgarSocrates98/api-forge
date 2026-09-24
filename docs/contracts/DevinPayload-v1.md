# `DevinPayload/v1`

Closed, frozen payload contract for sending API Forge instructions to Devin
Desktop, CLI or Cloud. It is an instruction artifact, not an execution or
authentication contract.

## Invariants

- `surface` is one of `desktop`, `cli`, `cloud`.
- `task_kind` is one of `discovery`, `planning`, `implementation`,
  `verification`, `review`, `handoff`.
- `permission_mode` uses Devin's documented CLI vocabulary and defaults to
  `normal`.
- `evidence_level` defaults to `declared`; generated payloads do not prove that
  Devin is installed, authenticated or available to the organization.
- `checks` are proposed verification commands. Their presence is not evidence
  that they ran successfully.
- `prohibited_actions` and `requires_human_confirmation` are explicit safety
  metadata; they do not override enterprise policy or CI branch protection.
- Version 2 must be a sibling contract rather than an in-place mutation.

## JSON shape

The authoritative schema is available through:

```text
apiforge contract schema DevinPayload/v1
```

Payloads are generated with:

```text
apiforge devin payload "<objective>" --surface cli --task-kind planning
```

The generated `prompt` always requires API Forge case loading, `next-step`,
evidence preservation, independent verification and the Outcome Brief handoff
shape. It explicitly disallows direct provider mutation.
