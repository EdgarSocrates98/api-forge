# AgentOpsTimeline/v1

Cross-ledger projection from `apiforge agentops timeline RUN`. Events merge
append-only run-ledger rows, telemetry spans and token ledger entries. Timestamp
order wins; rows without timestamps retain append order and add an unresolved
diagnostic.

| Field | Meaning |
|---|---|
| `events` | `AgentOpsTimelineEvent/v1` rows ordered by timestamp, then source, then id |
| `timestamp_coverage` | Fraction of events carrying a timestamp (`null` when there are no events) |
| `critical_path` | Event ids in timestamp order — emitted **only** when `timestamp_coverage == 1.0`; partial coverage leaves it empty and records the gap in `unresolved` (§62–§63: temporal order is never invented) |

Canonical schema: `apiforge contract show AgentOpsTimeline/v1`.
