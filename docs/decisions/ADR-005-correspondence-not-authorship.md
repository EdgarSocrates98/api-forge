# ADR-005: receipts prove correspondence, never authorship

## Status

Accepted — 2026-09-21.

## Context

Release evidence needs to answer "does this artifact still equal what was
produced?" without pretending to answer "who produced it?". Signing would add
key management the platform explicitly avoids; wall-clock timestamps would
break byte-determinism.

## Decision

`evidence emit` writes a receipt binding each declared artifact path to its
SHA-256, plus the policy hash. The receipt's `proves` field states exactly the
guarantee: correspondence between path and content at emit time. `emitted_at`
exists only when the caller passes `--now`; there is no implicit clock and no
signing key.

## Consequences

- Receipts are byte-reproducible on unchanged inputs — two emits differ only
  if content or the explicit `--now` differed.
- Verification re-hashes every listed path and names
  `AF-EVIDENCE-MISSING`/`AF-EVIDENCE-MISMATCH` per artifact.
- Authorship remains out of scope by construction; the threat model lists
  receipt tampering as mitigated by hash comparison only.
