# ContextUseRecord/v1

One recorded interaction between a consumer and a `ctx://` ref, derived from
the measured run ledger (`context *` -> `loaded`, `runtime role:<role>` ->
`assigned`, `context expand` -> `expanded`) or supplied by an eval fixture.

| Field | Meaning |
|---|---|
| `use_id` / `run_id` | Deterministic record id and the run it belongs to |
| `ref_uri` | The `ctx://sha256/...` ref interacted with |
| `action` | `loaded`, `assigned`, `expanded`, `cited` or `artifact`; only the last three count as consumed |
| `role` | Consuming role when known (null for capsule-level rows) |
| `bytes` | Bytes the interaction carried |
| `tokens` / `tokens_basis` | Observed token count when a transcript recorded it; `None` otherwise |

`cited` and `artifact` are caller-supplied and stay unresolved when absent;
the engine never infers them.
