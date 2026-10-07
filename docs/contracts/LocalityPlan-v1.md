# LocalityPlan/v1

`LocalityPlan/v1` is `apiforge workspace locality --target <repo> [--transitive]`.

| Field | Meaning |
|---|---|
| `target` | Repository being changed |
| `tiers[]` | `target`, `direct` (declared `depends_on`/`client_of`/`calls`/`deploys` neighbors) and `transitive` (next hop, `included: false` unless `--transitive`) |
| `excluded` | Workspace repositories not reached |
