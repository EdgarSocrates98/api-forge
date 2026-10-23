# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
## [0.2.3] - 2026-10-23

### Fixed

- Uninstall receipt re-persisted after context unregistration (emitted and
  archived receipts now agree on failure).

### Security

- Vendored `_installkit` 1.0.4: unsafe ledger keys surfaced in
  `status().drift.unsafe`; `doctor` marks them non-repairable.

## [0.2.2] - 2026-10-23

### Fixed

- `_forgecontext` v1.3.3 + `_installkit` v1.0.3 (vendored): `repair_context`
  reports malformed capability files per-file instead of crashing;
  context/install locks carry a unique ownership token; poisoned journals
  quarantine instead of wedging later ops; asset/ledger paths are
  validated before disk writes (`FORGE-INSTALL-UNSAFE-PATH`);
  `_atomic_write` preserves file modes.
- `install/render`: `knowledge/<rel>` references extracted from emitted
  docs now discard traversal refs (`..`, absolute, drive, backslash) —
  a crafted doc mention can no longer turn into an asset key that writes
  or unlinks outside the install root.
- `install --scope user` parity: `_register_context` is a no-op at user
  scope — `~/.forge/` is account-level state, matching the documented
  model and the sibling forges.
- A `BLOCKED` check on the mandatory context-registry component now marks
  the receipt `failed` (nonzero exit) — on install AND on uninstall.

## [0.2.1] - 2026-10-22

### Fixed

- `_forgecontext` v1.3.2: non-UTF-8 consumer docs (AGENTS.md / CLAUDE.md /
  AGENT_PROTOCOL.md) now refuse with named `FORGE-CONTEXT-CONFLICT` on
  install and uninstall — never a bare `UnicodeDecodeError` mid-write.

## [0.2.0] - 2026-10-22

### Added

- Install 2.0: `forge-context/v1` registry integration, transactional
  install/uninstall via vendored `_forgecontext` v1.3.1, consumer-doc managed
  blocks, evals classification, `qualified_ids` + `route()` support.

### Fixed

- `_txn_restore` journal path validation; interrupt-safe rollback;
  stale-lock `created_at` fallback (Windows); vendored `_installkit` v1.0.2 +
  `forge_bootstrap` v1.1.1 security backports (userinfo redaction, argv trim,
  empty-stdout smoke).

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



## [0.3.0] - 2026-10-23

### Fixed

- `ui._has_vcs_root`/`_cli_argv`: stray `forge.json` ancestor bound.
  Regression tests added.

## [0.1.6] - 2026-10-21

### Added

- Integrations cycle (lf-0030): `apiforge forge doctor` delegation lane to forge-doctor-api — evidence-backed discover/verify, closed argv scan, bounded output, env scrub, refusal/failure persistence, before/after compare; `api-forge-delegate-doctor` skill; Windows-safe doctor test fixture; portal bundle re-vendored with explorer pages.

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
