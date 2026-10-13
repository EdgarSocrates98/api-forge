# ADR-012: uv lock and MCP protocol freshness

## Status

Accepted — 2026-10-05.

## Decision

Commit `uv.lock` and validate it with a dependency-lock audit in CI. Keep the
library's bounded ranges in `pyproject.toml`; the lock governs this repository's
development, test and optional MCP environment, not downstream consumers.

The optional MCP extra requires `mcp>=2.2,<3`, matching the locally observed
SDK generation used to expose the 2026-07-28 protocol revision. The server stays
local stdio and read-only. Stateless HTTP, header routing and multi-round-trip
features are documented as unresolved until a local integration probe proves
them; no provider or network claim is inferred from the package version alone.

## Enforcement

- `uv lock --check` validates resolver consistency when uv is available;
- `scripts/lock_audit.py` validates committed metadata and artifact hashes with
  stdlib-only parsing, so CI does not need to install a second resolver;
- `scripts/mcp_protocol_probe.py` reports installed SDK/protocol observations;
- CVE/advisory freshness remains an external scanner gate.

## Rollback

Restore the prior lock snapshot and revert the MCP extra range. The core package
remains usable without the optional extra.
