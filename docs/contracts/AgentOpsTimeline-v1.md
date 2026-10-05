# AgentOpsTimeline/v1

Cross-ledger projection from `apiforge agentops timeline RUN`. Events merge
append-only run-ledger rows, telemetry spans and token ledger entries. Timestamp
order wins; rows without timestamps retain append order and add an unresolved
diagnostic.

Canonical schema: `apiforge contract show AgentOpsTimeline/v1`.
