# ADR-002: API-IR with provenance projections

## Status

Accepted — 2026-09-21

## Context

The MVP needs one representation that both the contract loader and the
FastAPI extractor can feed, and that the rule engine can judge. A naive merge
(one entry per route, "contract says X, code says Y") loses exactly the cases
that matter: duplicated routes, contract-only operations, code-only routes,
and ambiguous bindings.

## Decision

The API-IR keeps *projections*, not merged rows:

- `ApiOperation` is keyed by lowercase method + literal path (trailing slash
  is significant).
- Each side contributes zero, one, or many `Projection` entries — duplicates
  are never collapsed.
- Every projection carries `fact_id` and `SourceRef` (path, sha256, line,
  extractor), so any finding can be walked back to the byte range that
  produced it.
- The model records `input_hashes` for every input file and merges
  diagnostics from both producers, sorted deterministically.

## Consequences

- `AF-CONTRACT-001`/`AF-CODE-001`/`AF-CODE-002` are simple predicates over
  projection counts — the evidence model *is* the judgment model.
- "Unmatched" is a structural state (empty projection list), not an inferred
  one; rules can distinguish "provably absent" from "extraction uncertain".
- Persisted `api-ir.json` is self-contained evidence: a reviewer can verify
  every fact_id without re-running the pipeline.
- Adapters for other frameworks only need to emit code-side projections with
  provenance; the IR and rules stay unchanged.
