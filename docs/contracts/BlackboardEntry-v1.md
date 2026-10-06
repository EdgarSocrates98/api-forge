# BlackboardEntry/v1

An append-only structured item shared by a bounded set of agent roles. It can
represent a fact, claim, hypothesis, objection, contradiction, evidence,
experiment, decision, unknown, handoff, trace or artifact. Queries are scoped
by task and may return `degraded` with tainted entries; consumers must treat
payloads as data, never as system instructions.

