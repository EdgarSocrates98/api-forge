# P0 loop evidence

`RunStore.strategy_history()` reads `strategy_selected` events from the
append-only trajectory. Supervisor records the current fingerprint before
creating the control plane or invoking a capability. With sequence A, B, A,
A, the fourth admission returns `AF-GOV-LOOP-DETECTED`, and supervisor marks
the run `BLOCKED` with no invocation artifacts.

Focused proof:

```text
uv run pytest tests/governance/test_loop.py tests/contracts/test_agentic_governor.py tests/runtime/test_store_replay.py -q
```

Independent checks: `ruff check src tests`; `mypy src`.
