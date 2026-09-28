# LedgerRef/v1

`LedgerRef/v1` names one ref attributed by a `RunLedgerEntry/v1`.

| Field | Meaning |
|---|---|
| `uri` | The `ctx://sha256/…` ref |
| `label` | Readable handle copied from the capsule |
| `provenance` | Selection rule that included it (or `expand:on-demand`) |
| `size_bytes` | Bytes charged to this ref by the entry |

`apiforge economy explain <run_id>` maps each provenance to a reason without a
model call.
