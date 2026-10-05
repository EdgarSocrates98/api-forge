# Dependency locking and optional MCP

API Forge keeps bounded dependency ranges for downstream library consumers and
commits `uv.lock` for this repository's reproducible development and CI
environment. The lock is not a promise that every downstream installation uses
the same graph.

Local checks:

```bash
uv lock --check
python scripts/lock_audit.py
uv run --extra mcp python scripts/mcp_protocol_probe.py
```

The audit checks declared dependency membership, lock metadata and SHA-256
artifact hashes without resolving or downloading. CI also runs `pip check` and
the offline supply-chain audit. CVE/advisory freshness still requires an
external vulnerability database and remains explicitly unresolved locally.

The MCP extra is `mcp>=2.2,<3`. The protocol probe observes the installed SDK;
it does not claim stateless HTTP, header routing or multi-round-trip support
unless a local integration test produces that evidence. The core remains
usable without MCP.
