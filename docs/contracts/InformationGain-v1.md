# InformationGain/v1

`InformationGain/v1` is reported as `economy.information_gain` of a runtime
run, computed after L2.

| Field | Meaning |
|---|---|
| `level` | `low` (artifacts agree, nothing unresolved, confidence ≥ threshold), `high` (disagreement or unresolved items), `medium` otherwise |
| `reason` | Which condition decided |

The level explains the escalation triggers; it never overrides a
risk-required role.
