# ADR-004: SDD hash cascade

## Status

Accepted — 2026-09-21.

## Context

SDD artifacts are written in phases. If an upstream artifact (say `contract`)
changes after downstream phases were validated, every conclusion derived from
it is silently stale — reviews, plans and builds would rest on content nobody
re-checked.

## Decision

Every phase except `discover` declares `upstream: {path, sha256}`. `sdd stamp`
computes the upstream content hash and rewrites **only that frontmatter line**;
`sdd check` re-hashes and reports `AF-SDD-UPSTREAM-STALE` on divergence and
`AF-SDD-PHASE-ORDER` when upstream does not point backwards. Text hashes
normalize CRLF to LF so line-ending noise cannot cause false staleness.

## Consequences

- Staleness is detected, not assumed; a changed upstream blocks downstream
  `done` until re-stamped and re-checked.
- `stamp` is byte-conservative: it never rewrites unrelated formatting, BOM or
  line endings, so stamps do not dirty files.
- The cascade is cheap to verify offline — no timestamps, no external state.
