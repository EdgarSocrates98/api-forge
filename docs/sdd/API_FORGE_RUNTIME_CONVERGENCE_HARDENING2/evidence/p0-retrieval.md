# P0 retrieval evidence

L3 hybrid writes its weighted lexical/semantic score to
`signals.effective_score` and sorts by that value. L4 writes weighted
lexical/semantic/graph score and derives graph contribution from
`graph_depth`; `selected_pack` no longer acts as graph evidence. Adaptive
sufficiency and `RetrievalStep.top_score` read the same effective score, while
`raw_top_score` preserves source-scale diagnostics.

Focused proof:

```text
uv run pytest tests/knowledge/test_levels.py -q
uv run apiforge evals retrieval --detail-level full
```

Independent checks: `ruff check src tests`; `mypy src`.
