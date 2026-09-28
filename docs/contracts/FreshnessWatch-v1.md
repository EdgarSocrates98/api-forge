# FreshnessWatch/v1

`FreshnessWatch/v1` is `apiforge knowledge watch --manifest <json> --now <iso>` (§96). It compares every pack with a local upstream manifest written by the separate refresh workflow; it never fetches.

| Field | Meaning |
|---|---|
| `now` | Explicit clock used for expiry and window checks |
| `manifest_sha256` | sha256 of the manifest bytes that were compared |
| `entries[]` | `{pack_id, domain, state, upstream, declared_fingerprint, upstream_fingerprint, declared_version, upstream_version, reasons, next_action}` |
| `entries[].state` | `fresh`, `refresh_needed` (fingerprint, version, expiry or window), `unknown` (no metadata) or `unresolved` (no comparable manifest entry) |
| `refresh_needed` | Pack ids that need the refresh workflow |
| `fetches` | Always `false` |
