# protocol and supply-chain evidence

MCP documentation now targets the official 2026-07-28 revision and marks the
stdio/read-only implementation plus stateless HTTP/header behavior separately.
The optional extra is `mcp>=2.2,<3`; `mcp_protocol_probe.py` observes the
installed SDK without network access. `uv.lock` is committed and
`lock_audit.py` checks declared package membership and SHA-256 artifacts in CI.

External vulnerability-database freshness remains unresolved by design.

Observed checks:

- `uv run python scripts/lock_audit.py` — package count `68`, hashed registry packages `67`, `ok=true`.
- `uv run --extra mcp python scripts/mcp_protocol_probe.py` — SDK `2.3.0`, latest protocol `2026-07-28`, observed.
- `uv run python scripts/supply_chain_audit.py` — `ok=true`; external CVE database and local `pip check` availability remain unresolved outside CI.
- `uv run apiforge mcp benchmark --repeats 1 --detail-level full` — `10` sampled tools, `unresolved=[]`; output basis remains `estimated` token counts.
