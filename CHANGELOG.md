# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.1] - 2026-10-18

### Fixed
- Portal vendored 2.1 final (Cycles 0-6)

## [Unreleased]

### Fixed

- `apiforge-mcp` / `apiforge mcp` without the `mcp` extra now exits 2 with
  the guided `AF-MCP-OPTIONAL-UNAVAILABLE` refusal instead of a raw
  traceback (unrelated `RuntimeError`s still propagate); contract tests
  cover the refusal path.
- `doc_manifest._check_links` now verifies `#fragment` anchors on
  tag-pinned repo URLs (they were silently dropped), exempts GitHub line
  refs (`#L10`, `#L10-L20`) and rejects `%5C` backslash escapes.

### Changed

- Packaging metadata: `readme` field wired, classifiers corrected
  (Python 3.13 dropped — CI tests 3.12 only), `project.urls` added.
- README/README.pt-BR install instructions point to the real
  `apiforge-af` dist; links/images pinned to `v0.1.0` absolute URLs so
  the PyPI-rendered page resolves.
- `pip install apiforge-af` section added to the README.

## [0.1.0] - 2026-10-15

### Added

- Forge Lab emitter producing `forge/BenchmarkResult/v1` receipts from the
  §28 scenario catalog (cyc9-06).
- GitHub experience files: CONTRIBUTING, CODE_OF_CONDUCT, SUPPORT,
  issue/PR templates, DCO requirement (cyc10-02).

### Changed

- `cryptography` pinned `>=50,<51` — fixes CVE-2025-* findings in the
  bundled 46.0.7 line (Ed25519 API usage only).
- Vendored installkit/ui-kit/portal assets refreshed from canonical
  the-forge (cyc8-02, cyc9-10).
