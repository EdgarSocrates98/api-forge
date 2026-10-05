# P0 recovery evidence

`run_bounded` now classifies each failure and calls `decide_recovery` before
starting another worker attempt. `retry` continues only while the runtime
retry ceiling remains; `replan`, `fallback`, `escalate` and `stop` return a
typed recovery receipt to the supervisor. Invalid adapter output proves the
no-retry path; provider/tool failure proves bounded retry then fallback.

Focused proof:

```text
uv run pytest tests/governance/test_recovery.py tests/runtime/test_scheduler.py -q
```

Independent checks: `ruff check src tests`; `mypy src`.
