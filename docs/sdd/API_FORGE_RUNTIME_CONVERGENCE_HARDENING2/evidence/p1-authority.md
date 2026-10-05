# P1 authority evidence

`AgentRequest` now carries `authority_subject`, `delegated_from` and
`delegated_scope`. The runtime authorizes the fixed adapter boundary separately
from each requested tool, so a role does not inherit orchestrator grants.
Delegation edges are declared in `tool_risk.yaml`; out-of-scope and undeclared
delegations deny with a cataloged refusal.

`apiforge_call` keeps its gateway authorization, resolves the target, then
authorizes the target against the known MCP registry and the effective
subject's `allowed_targets` before invoking the inner function. Unknown target
names deny before signature binding; inner domain gates remain unchanged.

Focused proof:

```text
uv run pytest tests/trust/test_tools.py tests/runtime/test_tool_authorization.py tests/agentops/test_tool_host_economy.py -q
```

Independent checks: `ruff check src tests`; `mypy src`.
