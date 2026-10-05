# BudgetReconciliation/v1

§22 post-run comparison: estimated vs observed for tokens, cost, tool
calls and elapsed time, with per-axis calibration error.

| Field | Meaning |
|---|---|
| `scope` | What is reconciled (`run:<id>`) |
| `estimated` / `observed` | The two `ReconciliationAxis` sides |
| `calibration_error` | `(observed - estimated) / estimated` per axis — overestimation is negative |
| `unresolved` | Axes missing on either side, or a zero estimate against a positive observation |

Invariant — NO GAIN WITHOUT MEASUREMENT: an axis absent from either side
is named unresolved rather than silently scored as perfect or zero; an
estimate of `0` with a nonzero observation cannot express a ratio and is
unresolved too.
