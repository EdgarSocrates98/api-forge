# LabReport-v1

§28 experimental scenario catalog emitted by `apiforge lab scenarios`.

| Field | Meaning |
|---|---|
| `scenarios` | `LabScenario` cells with coverage states |
| `totals` | `scenarios`/`covered`/`declared_gap` counts |
| `unresolved` | missing catalog kinds or dead pointers, named |

Invariant: every cell either points at a real fixture/eval/proof or names
its declared gap — a cell with neither refuses `AF-LAB-CELL-UNDECLARED`.
The lab is opt-in; nothing here is required for basic use.
