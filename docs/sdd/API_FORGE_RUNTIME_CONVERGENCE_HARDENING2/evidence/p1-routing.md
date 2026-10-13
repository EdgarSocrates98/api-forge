# P1 routing evidence

`ModelRouteInputs.task_class` selects matching scorecards; missing cards stay
unresolved and do not fabricate quality. `route_model_shadow` sends the
candidate and declared legacy result through the existing `model_routing`
Decision Plane route. The local route writes a `ShadowRecord` and returns
`governing=legacy`; it never promotes the candidate.

Focused proof:

```text
uv run pytest tests/runtime/test_model_router.py -q
uv run apiforge evals model-routing --detail-level full
```

Independent checks: `ruff check src tests`; `mypy src`.
