# Policy contract

API Forge decides whether an action may run through **policy as data**: a
closed-schema YAML catalog loaded as `Policy`, evaluated by the pure function
`decide`. No procedural logic is hardcoded per verb.

## Autonomy classes

`read_only` · `local_reversible` · `sensitive` · `external_mutation` ·
`destructive` · `irreversible`

- `read_only` analysis is automatic.
- `local_reversible` work happens only inside sandbox/worktree copies.
- `sensitive`, `external_mutation` require declared gates.
- `destructive` requires exact `target`, `impact`, a dry-run or a named reason
  it is impossible, `rollback` and `confirmation` — all in `detail`.
- `irreversible` is denied by default.
- An action with no declared class is ambiguous and **denied**, never inferred.

## Outcomes

`decide` returns `{outcome, rule, reason_code, missing_requirements,
satisfied_by, subject}`:

- `allow` — no rule matched and the class default permits, or a gate's
  requirements were all supplied in `detail` (`satisfied_by` records which).
- `gate` — the class requires fields the request did not supply;
  `missing_requirements` names them. The engine never self-satisfies a gate.
- `deny` — a deny rule matched or the class default forbids; `rule`/`reason_code`
  name the cause.

Deny rules are evaluated first-match before class defaults. Everything is
deterministic and serializable.

## Codes

| Code | Meaning |
|---|---|
| `AF-POLICY-SCHEMA` | policy document violates the closed schema (unknown keys, bad class, malformed rule) |
| `AF-POLICY-NOT-FOUND` | requested policy file absent |
| `AF-POLICY-CLASS-UNKNOWN` | action declared a class outside the six-class vocabulary |
| `AF-POLICY-DENY` | a deny rule matched the verb/arguments |
| `AF-POLICY-GATE` | class default requires fields the request lacks |
