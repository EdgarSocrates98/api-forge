# VerificationPlan/v1

`VerificationPlan/v1` is `apiforge verify plan --changed F... --risk R [--breaking]`.
It never executes anything.

| Field | Meaning |
|---|---|
| `risk` / `level` | Risk class and ladder level: micro V1, low V2, medium V4, high V5; a breaking verdict raises to at least V4 |
| `tests[]` | `{path, reasons}` — `capsule-test-ref:<target>`, `mentions:<symbol>`, `imports:<module>`, `changed` |
| `total_tests` | Test files discovered, for comparison with the selection |
| `commands` | What a host or CI would run for the level |
| `skipped_levels` | Levels above the chosen one |
| `reasons` | Why the level was chosen, including `no-impacted-tests-found` escalation to V5 |
| `executes` | Always `false` |
