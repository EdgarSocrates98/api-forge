# P0 truthfulness evidence

Focused proof: `uv run pytest tests/agentops/test_inspect_waste.py -q` passed
with the new no-observation and partial-observation cases. `uv run apiforge
evals agentops --detail-level full` passed all four corpus cases after the
fixture declared `model_call_id`.

The implementation emits `tokens=unresolved` with a null value when no
run-ledger row reports observed tokens, emits `tokens=partial` when only some
eligible rows report usage, and emits `token_observation_coverage` when the
eligible-row denominator is known. Model call counts use unique
`model_call_id`; token entries and provider attempts remain separate.
