# Decision governance

`apiforge governance decision-check` separates proposal from authorization.
Read-only proposals may be allowed; sensitive, destructive, irreversible and
external-mutation proposals require evidence plus a human `ApprovalGate`.
The default policy disallows external mutation even if a proposal contains
approval-like text.

```text
apiforge governance decision-check --request request.json --root .
apiforge governance decision-check --request request.json \
  --approval approval.json --policy policy.json --root .
```

Results are appended to `.apiforge/governance/decision-gates.jsonl`. The MCP
`decision_check` tool uses the same service. `review` and `block` are explicit
outcomes; neither authorizes a side effect.
