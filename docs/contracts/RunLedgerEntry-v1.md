# RunLedgerEntry/v1

`RunLedgerEntry/v1` (`schema: apiforge/run-ledger-entry/v1`) is an
attribution row appended to `<root>/.apiforge/economy.jsonl`.

| Field | Meaning |
|---|---|
| `run_id` | Capsule run the row belongs to |
| `verb` | Emitting verb, e.g. `context capsule`, `context expand` |
| `detail_level` | Detail level of the emission |
| `source` | `graph`, `contract`, `code`, `knowledge`, `filesystem` or `envelope` |
| `cost` | `CostVector/v1` |
| `refs` | `LedgerRef/v1` entries attributed by this row |
| `recorded_at` | Optional append-time stamp (§64). `run_ledger.append()` stamps the write instant when the caller supplies none; rows written before the field existed stay timestamp-free and the timeline reports the coverage gap |

Rows are written with `payload_bytes: 0` because the transport bytes of the
same emission are recorded by the verb's legacy row; `economy report` totals
are therefore unchanged. `economy stats` reads legacy rows into a separate
`legacy` bucket and skips malformed lines with a counted diagnostic.

`economy stats` aggregates these rows with `token_coverage = {status, observed_rows, eligible_rows}`; a partial measurement is never reported as an observed total. Runtime role rows are auditable: a row that cannot be persisted is counted in `persist_failures` and reported as `AF-ECONOMY-LEDGER-PERSIST`.
