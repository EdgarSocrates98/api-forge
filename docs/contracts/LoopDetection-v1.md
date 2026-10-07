# LoopDetection/v1

§27 repeated-strategy detection. `strategy_fingerprint` is the sha256
prefix of the strategy's canonical JSON — identical plans hash
identically regardless of prose.

| Field | Meaning |
|---|---|
| `strategy_fingerprint` | Canonical hash of the latest strategy |
| `repeats` | Extra occurrences inside the trailing window |
| `window` | How many recent fingerprints were inspected |
| `blocked` | `true` when `repeats >= max_repeats` — the cycle is refused |
| `action` | Governed response recorded with the detection: `stop`, `replan`, `fallback` or `human` |
| `code` | `AF-GOV-LOOP-DETECTED` when blocked |

Runtime enforcement records `strategy_selected` in the append-only run
trajectory before any capability invocation. Current policy selects `stop`,
so a repeated strategy returns `BLOCKED` and spends no invocation budget.
Other actions remain contract values for governed future adapters; runtime
must not silently continue when such an action lacks an implementation.
