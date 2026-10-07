# ReplayReport/v1

`ReplayReport/v1` is `apiforge evals replay --root R | --corpus C [--profile P]`:
stored routing decisions re-planned under the current policy without calling
a provider.

| Field | Meaning |
|---|---|
| `runs[]` | `{run, profile, status same, changed or unresolved, removed_required_roles, trimmed_before, trimmed_after, effective_before, effective_after, reason, decisions[]}` |
| `changed` / `unresolved` | Counts; a run without `routing.json`/`economy.json` is `unresolved` (`AF-REPLAY-RUN-INCOMPLETE`) |
| `removed_required_roles` | Risk-required roles the new policy would drop — must be 0 |
| `decisions_changed` / `decisions_unresolved` | Counts over `runs[].decisions[]` (`unresolved` also counts `absent`) |
| `policies` | `decision name → sha256:` hash of the policy file the decision was re-derived under (§86) |
| `passed` | `removed_required_roles == 0` |

## `ReplayDecision/v1` — the §83/§87 decision chain

Each run replays five control-plane decisions in chain order —
`loop`, `model_route_shadow`, `tool_authorization`, `trust_admission`,
`recovery` — against the artifacts the run persisted (`events.jsonl`
fingerprints, `model-route-shadow.json` inputs, `run.json`,
`role-context.json`, `recovery-receipts.json`). Statuses:

- `same` — the stored verdict reproduces under the current policy;
- `changed` — policy or data drift flips the verdict (`AF-REPLAY-DECISION-CHANGED`);
- `unresolved` — the run lacks the inputs to re-derive it (no guessing, §85);
- `absent` — the run never produced that decision.

Only control-plane artifacts are re-derived; replay never touches LLM text.
