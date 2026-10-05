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
| `code` | `AF-GOV-LOOP-DETECTED` when blocked |
