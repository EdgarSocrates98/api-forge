# ADR-009: knowledge-pack docs are generated, never authored

## Status

Accepted — 2026-09-26.

## Context

The spec asks every knowledge pack to carry index, quick-reference,
concepts, patterns, anti-patterns, recipes, troubleshooting and evals.
Hand-writing 37 x 8 documents invites stale prose and unsourced claims —
the exact failure the packs exist to prevent.

## Decision

`scripts/gen_pack_docs.py` derives every pack doc from artifacts that
already carry the truth: catalog rules (title, severity, rationale,
remediation, reference), `source_authority.yaml`, dispatch verbs and the
documented error codes. Rule-bearing packs without hand-written evals get
declarative probes generated from rule titles; a hand-written
`evals.yaml` is never overwritten. `check_packs` requires the full doc
set and flags rule-bearing packs with empty evals — enforced by the
release gate.

## Consequences

- Docs cannot drift ahead of the rules: regenerate after catalog changes.
- Packs with no executable rules honestly say "source index only" instead
  of fabricating patterns.
- Evals remain declarative data for external runners — the project still
  never calls a model.
