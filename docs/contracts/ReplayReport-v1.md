# ReplayReport/v1

`ReplayReport/v1` is `apiforge evals replay --root R | --corpus C [--profile P]`:
stored routing decisions re-planned under the current policy without calling
a provider.

| Field | Meaning |
|---|---|
| `runs[]` | `{run, profile, status same, changed or unresolved, removed_required_roles, trimmed_before, trimmed_after, effective_before, effective_after, reason}` |
| `changed` / `unresolved` | Counts; a run without `routing.json`/`economy.json` is `unresolved` (`AF-REPLAY-RUN-INCOMPLETE`) |
| `removed_required_roles` | Risk-required roles the new policy would drop — must be 0 |
| `passed` | `removed_required_roles == 0` |
