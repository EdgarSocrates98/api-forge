# TokenLedgerEntry/v1

One usage row in the §19 pipeline — who consumed what, on which basis,
with provenance. Rows persist append-only under
`.apiforge/economy/token_usage/<run_id>.jsonl`.

| Field | Meaning |
|---|---|
| `entry_id` | Deterministic `usage:<sha256[:16]>` of run+accounting+timestamp; replay produces the same id |
| `run_id` | Owning run |
| `task_id` / `agent` | Optional attribution scope for task/agent rollups |
| `model_call_id` | Optional provider/model span correlation id; absent ids remain unresolved for call attribution |
| `accounting` | The `TokenAccounting/v1` payload |
| `recorded_at` | Caller-declared timestamp |
| `provenance` | Source labels (`transcript:<path>`, `caller:declared-estimate`, …) |
