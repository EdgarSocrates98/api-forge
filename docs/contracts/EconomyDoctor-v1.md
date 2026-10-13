# EconomyDoctor/v1

`EconomyDoctor/v1` is `apiforge economy doctor` (also `apiforge doctor --economy`).

| Field | Meaning |
|---|---|
| `checks` | Checks performed: cache, default profile, capsule usage, output mode, shared cache, knowledge freshness, token receipts, escalation rate, repeated parsing |
| `findings[]` | `{code, severity (info or warning), detail, unlock}` |
| `status` | `attention` when any warning exists, else `ok` |
