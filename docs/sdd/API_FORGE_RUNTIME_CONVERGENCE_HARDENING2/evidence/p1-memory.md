# P1 memory evidence

V1: stale state → score freshness `0.0`; no expiry field required.

V2: expiry ≤ query clock → derived `expired`; destructive query excludes row.

V3: runtime constraints → explicit structured runtime matcher; query terms ⊥
runtime evidence.

V4: taint ∈ MemoryTrust → default context admission excludes row and preserves
tainted diagnostic.

V5: applicable ∧ trusted ∧ fresh ∧ contradictory → `MemoryConflict/v1`.
Read-only outcome `review`; destructive outcome `quarantine` + exclude pair.

Proof:

- `uv run pytest tests/memory/test_hardening2.py -q --basetemp E:/pytest-apiforge-hardening2-memory2`
- result: `5 passed`
- `uv run ruff check src tests/memory/test_hardening2.py` → pass
- `uv run mypy src/apiforge/memory src/apiforge/contracts` → pass

Artifacts:

- `src/apiforge/memory/matching.py`
- `src/apiforge/memory/conflicts.py`
- `src/apiforge/contracts/agentic_memory.py`
- `tests/memory/test_hardening2.py`

Unresolved: semantic contradiction beyond deterministic scalar paths remains
outside local proof; provider/runtime freshness remains external.
