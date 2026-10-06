# ADR-001: Deterministic core, no model in the analysis path

## Status

Accepted — 2026-09-21

## Context

API Forge exists to produce *verifiable* evidence about APIs. An analysis
whose output varies between runs — or that depends on a model's sampling —
cannot be audited, diffed, or gated on. The design specification states the
budget contract: "Resultado correto, verificável e reproduzível por token
consumido."

## Decision

The analysis core is deterministic and offline:

- Hashing is SHA-256 over raw bytes; `stable_id` derives from sorted, compact
  JSON.
- Serialization is sorted-key UTF-8 JSON with one trailing newline, written
  via sibling temp file + atomic replace.
- All ordering (operations, projections, findings, diagnostics) is explicit
  and total — never set-iteration order.
- No wall-clock timestamps appear in persisted artifacts; any future time
  field must be supplied explicitly (e.g. `--now`).
- No model or cloud SDK may be imported by `src/apiforge`; the release gate
  enforces this (`scripts/check_mvp_release.py`).

## Consequences

- Byte-reproducibility is a testable property (e2e and release gate run the
  same fixture twice and compare bytes).
- Every nondeterminism risk (dict order, filesystem order, time) must be
  pinned at the point it enters — inside the core, not at the CLI.
- Ambiguity becomes a named `unresolved` diagnostic rather than a guess; the
  product of the pipeline is evidence, not narrative.
- A future agentic layer may sit *above* the core, but it consumes artifacts;
  it cannot change how facts were extracted.
