# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
## [0.1.5] - 2026-10-21

### Changed

- Cycle 13 (graph): Graph Studio vendored update — P0 physics fix (NaN blow-up on hubs/star), scalable visualization modes (overview/explore/full), navigation, inspectors and bounded analysis; post-lf-0023 portal explorer assets re-vendored; security/accessibility/reliability hardening.

## [0.1.3] - 2026-10-20

### Changed
- Cycle 12 portable distribution: `_data/{knowledge,evals,tests/fixtures}` +
  host/portal assets packaged in the wheel; resolvers env → cwd →
  repo-marker → packaged (`importlib.resources`, zipimport-safe).
- `pack_dir` refuses traversal in `knowledge <domain>` (`AF-KNOW-DOMAIN`),
  including bare `..`/`.`; CLI and MCP call sites wired through it.
- `forge.json.distribution` corrected to the real PyPI name `apiforge-af`.
- New SDD feature record `API_FORGE_CYCLE12_PORTABLE_DIST` (retroactive).

## [0.1.2] - 2026-10-18

### Changed
- Portal 2.2 vendored generation (44-asset frontend, telemetry,
  py3.10-safe server); hardened PyPI pipeline (build-once/
  publish-same-artifact, version gate, post-publish verify)

## [0.1.1] - 2026-10-18

### Fixed
- Portal vendored 2.1 final (Cycles 0-6)

## [Unreleased]

## [0.1.4] - 2026-10-20

### Changed
- Cycle 12.1: vendored `scripts/forge_bootstrap.py` re-stamped to the canonical ruff-formatted source; `install.windows.sh` added as the Git Bash/MSYS install route; CI gains a `bash -n` gate for it; `docs/installation/account-installation.md` documents the Windows-without-PowerShell path.

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
