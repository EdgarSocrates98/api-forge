# ADR-010: v1 autonomy modes map onto mode x action class

## Status

Accepted — 2026-09-22.

## Context

`prompt_evo_api_forge_v1.md` asks for five autonomy modes:
`observe`, `recommend`, `sandbox`, `approved`, `continuous`. The
implementation shipped three: `observe`, `supervised`, `continuous`. The
divergence is real and was silent until the v1-closure audit.

The two vocabularies cut the same space along different axes. v1's five
names conflate *execution posture* (does anything run?) with *permission*
(which action classes may proceed). The implementation keeps posture in
`AutonomyMode` and permission in the policy engine's action classes
(`read_only`, `local_reversible`, `sensitive`, `external_mutation`,
`destructive`, `irreversible`).

## Decision

Keep the three persisted modes. Accept the v1 names as aliases resolved
through `V1_MODE_MAP` in `autonomy/modes.py`:

| v1 mode | resolves to | because |
|---------|-------------|---------|
| observe | observe | identical |
| recommend | observe | a proposal is a ledger entry; nothing executes |
| sandbox | supervised | `local_reversible` auto-executes; gates halt |
| approved | supervised | `sensitive`/`external_mutation` proceed only when the caller supplies the gate's declared requirements |
| continuous | continuous | identical |

`parse_mode` resolves the alias; `set_mode` records `requested` in the
ledger whenever the requested name differs from the persisted mode, so
the mapping stays auditable rather than silent.

## Alternatives rejected

- **Migrate to the literal five modes.** Splits one axis in two and
  creates mode x class ambiguity (what is `sandbox` + `destructive`?),
  while migrating vocabulary across dispatch, runbooks, docs and tests
  for zero behavioral gain.
- **Do nothing.** Silent divergence from the spec is exactly what this
  feature exists to close.

## Consequences

- The persisted vocabulary differs from v1's literal names — mitigated
  by this ADR and `V1_MODE_MAP` making the correspondence explicit.
- No behavioral migration; `mode.json` files written before remain valid.
