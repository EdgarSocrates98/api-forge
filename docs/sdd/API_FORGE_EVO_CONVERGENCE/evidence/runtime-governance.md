# runtime governance evidence

The supervisor now creates `RunGovernanceContext/v1` after routing/economy
normalization and before optional escalation, debate or shadow work. It writes
`governance-context.json`, a trajectory event and the context id on `AgenticRun`.
Postflight context now records declared recovery decisions and a strategy-loop
fingerprint; no error or loop state becomes an implicit success.

Observed checks:

- `uv run pytest -q --basetemp E:/pytest-apiforge-evo-convergence tests/runtime/test_supervisor.py::test_supervisor_persists_governance_context_before_run_expansion tests/contracts/test_agentic_governor.py tests/governance/test_governor.py` — **16 passed**.
- Existing supervisor/governance/e2e slice — **63 passed**.
- Focused lab, trust and supervisor regression — **31 passed**.
- `uv run mypy` on the changed runtime and contract modules — **no issues**.

Missing confidence, evidence completeness and context sufficiency remain named
unresolved signals in the receipt; they are not inferred from task text.
