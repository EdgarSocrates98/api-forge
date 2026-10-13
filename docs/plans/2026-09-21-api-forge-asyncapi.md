# Plan 12 — AsyncAPI adapter

**Goal:** `model asyncapi --path doc.yaml` reads AsyncAPI 2.x and 3.x documents
offline → facts `asyncapi.server`/`asyncapi.channel`/`asyncapi.operation`.
`$ref` targets are recorded by pointer, never dereferenced; unknown versions
become `AF-ASYNC-VERSION` diagnostics.

- [ ] T1: `adapters/asyncapi/` — channels (2.x publish/subscribe → action send/receive; 3.x operations), servers, `$ref` → `AF-ASYNC-UNRESOLVED`
- [ ] T2: CLI `model asyncapi` + tests + docs/gate parity (AF-ASYNC codes)
