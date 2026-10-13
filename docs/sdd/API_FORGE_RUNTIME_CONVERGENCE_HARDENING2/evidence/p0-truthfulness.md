# P0 truthfulness evidence

Focused proof: `uv run pytest tests/agentops/test_inspect_waste.py
tests/context/test_quality.py -q` passed with the new no-observation,
partial-observation and missing-required-evidence cases. `uv run apiforge
evals agentops --detail-level full` passed all four corpus cases after the
fixture declared `model_call_id`.

The implementation emits `tokens=unresolved` with a null value when no
run-ledger row reports observed tokens, emits `tokens=partial` when only some
eligible rows report usage, and emits `token_observation_coverage` when the
eligible-row denominator is known. Model call counts use unique
`model_call_id`; token entries and provider attempts remain separate.

Context Quality now keeps every explicitly declared required evidence URI in
the recall denominator, even when absent from the selection, and emits
`selected_evidence_utilization` as a separate selected-set metric.
