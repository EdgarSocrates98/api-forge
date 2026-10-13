# P1 AgentOps evidence

V1: coverage metrics never fill missing basis with zero.

V2: timeline merges ledger, span and token events; timestamp absence remains
unresolved and ledger append order remains visible.

Proof:

- `uv run pytest tests/agentops/test_inspect_waste.py -q --basetemp=E:/pytest-apiforge-hardening2-agentops`
- result: `19 passed`
- focused extension with timeline/coverage: `20 passed`
- `uv run ruff check src tests` → pass
- `uv run mypy src` → pass

Artifacts:

- `src/apiforge/agentops/inspect.py`
- `src/apiforge/agentops/timeline.py`
- `src/apiforge/contracts/agentops_report.py`
- `src/apiforge/cli.py`
- `src/apiforge/mcp/tools.py`

Unresolved: monetary cost remains unresolved without declared provider pricing;
ledger rows without timestamps cannot be placed on wall-clock axis.
