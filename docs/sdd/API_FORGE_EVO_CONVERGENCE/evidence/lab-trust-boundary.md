# lab and trust-boundary evidence

All `13` declared lab scenarios now have real local fixture/proof pointers;
`uv run apiforge lab scenarios` returns `covered=13`, `declared_gap=0` and
`unresolved=[]`. Proofs label deterministic scope and keep production,
provider, broker and datastore claims external.

The six compact MCP gateways now pass through the `mcp-gateway` risk-policy
subject. Unknown subjects fail closed with `AF-TOOL-AUTHZ-DENIED`; gateway
authorization does not erase inner tool policy checks.

Runtime adapter crossings now authorize `agent-invocation` under
`api-orchestrator`; requested `AgentRequest.tool_names` require their own
declared profiles. L2 retrieval traverses a declared bounded graph with node
and depth provenance. Context evals include one-ref-at-a-time counterfactual
ablation and keep evidence recall unresolved without declared required refs.

Observed checks:

- Focused lab, trust and gateway suite — **31 passed**.
- Ruff check/format and mypy on changed gateway, supervisor and lab tests — **passed**.
