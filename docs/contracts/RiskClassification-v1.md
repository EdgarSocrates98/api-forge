# RiskClassification/v1

`RiskClassification/v1` (`schema: apiforge/risk-classification/v1`) is the
output of `apiforge sdd classify`.

| Field | Meaning |
|---|---|
| `risk_class` | `micro`, `low`, `medium` or `high` |
| `sdd_profile` | Minimum SDD profile: `micro`, `quick`, `standard`, `critical` (`migration` when cross-repo) |
| `signals` | Deterministic signals: `contract:<verdict>`, `path:<p>`, `keyword:<w>`, `cross-repo:<n>`, `docs-only` |
| `unresolved` | `AF-SDD-RISK-UNRESOLVED` when no signal classified the change (defaults to `medium`) |

With `--write <feature dir>`, `risk_class` and `risk_signals` are recorded in
the feature's `intent.md` frontmatter; `sdd check` then refuses a declared
profile below the minimum with `AF-SDD-PROFILE-BELOW-RISK`.
