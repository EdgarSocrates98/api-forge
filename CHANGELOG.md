# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
