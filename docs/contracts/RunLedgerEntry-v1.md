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

Rows are written with `payload_bytes: 0` because the transport bytes of the
same emission are recorded by the verb's legacy row; `economy report` totals
are therefore unchanged. `economy stats` reads legacy rows into a separate
`legacy` bucket and skips malformed lines with a counted diagnostic.
