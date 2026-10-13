# VerificationEscalation/v1

`VerificationEscalation/v1` is `apiforge verify escalate` (§99): static → test → stop; read-only runtime only after an inconclusive test. It never executes the step.

| Field | Meaning |
|---|---|
| `static` / `test` / `runtime` | Verdicts in; `test` can come from a `TestSlice/v1` via `--test-slice` |
| `action` | `run_tests`, `escalate`, `stop` or `unresolved` |
| `next_mode` | `test`, `live_read_only` or null; never a mutation |
| `reason` | The transition taken |
| `test_evidence` | Failing tests or pass count taken from the slice |
| `unresolved` | `AF-VERIFY-ESCALATE-EXHAUSTED` when test and runtime are both inconclusive |
