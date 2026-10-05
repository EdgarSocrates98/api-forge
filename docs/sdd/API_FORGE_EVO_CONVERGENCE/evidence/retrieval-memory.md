# retrieval and memory evidence

Model routing now treats risk, budget, freshness and evidence correctness as
declared constraints. Champion candidates are selected by default; challengers
require `allow_challenger=true`. Retrieval L3 can add candidates from a full
local semantic pool and reports passage provenance. Memory queries support
structured environment compatibility and configurable term coverage (default
`0.5`, strict all-term matching via `1.0`).
L2 now traverses an explicit bounded graph directory; absent graph evidence is
reported unresolved instead of being mislabeled as sibling graph retrieval.

Observed checks:

- Focused model/router, retrieval and memory suites — **38 passed**.
- Ruff check and mypy on changed model, knowledge and memory modules — **passed**.
- Ruff format on changed files — **passed**.
- Graph traversal regression — **9 passed** in `tests/knowledge/test_levels.py`.

No provider, vector database or semantic API was called. The hash-feature
adapter is a deterministic local candidate generator, not a claim of embedding
quality.
