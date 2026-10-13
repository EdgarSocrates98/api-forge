# Release evidence

Pending final convergence. The proof will link the local release receipt,
lock/SBOM audit, SDD check, tests and explicit external gates.
# Release evidence

R1: local release gates pass; external freshness stays unresolved.

Proof:

- `uv run python scripts/supply_chain_audit.py` → `ok: true`, `failed: 0`,
  `unpinned: []`, vendor parity PASS, corpus `29/195`, MCP surface `152`
- `uv run python scripts/check_release.py` → pass
- `uv lock --check` → pass
- `uv run apiforge evals agentops --detail-level full` → `4/4` pass
- `uv run apiforge mcp audit --surface full --detail-level full` → pass,
  findings `[]`, accepted overlap `1`
- `uv run apiforge mcp benchmark --repeats 2 --detail-level full` → `10/10`
  samples, no unresolved benchmark findings
- `uv run apiforge lab scenarios` → `21/21` catalog cells covered
- `uv run pytest --basetemp=E:/pytest-apiforge-hardening2-final2 -q` →
  `1751 passed, 2 skipped`
- `uv run ruff check src tests` → pass
- `uv run ruff format --check src tests` → pass
- `uv run mypy src` → pass

Artifacts:

- `scripts/supply_chain_audit.py`
- `docs/mcp-compliance.md`
- `docs/decisions/API_FORGE_HARDENING2_GAP_MATRIX.md`
- `docs/decisions/API_FORGE_HARDENING2_OUTCOME_BRIEF.md`

Unresolved: external CVE/advisory feed, pip-check outside uv interpreter,
optional FastMCP SDK handshake, provider freshness, deployment safety,
production SLOs and external CI runner health. Local receipts do not promote
these claims.
