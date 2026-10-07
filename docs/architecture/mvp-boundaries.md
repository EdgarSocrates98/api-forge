# MVP boundaries

Language: [English](mvp-boundaries.md) · [Português (Brasil)](mvp-boundaries.pt-BR.md)

The vertical slice is deliberately bounded. Everything outside this list is
out of scope for the MVP and must surface as an `unresolved` diagnostic or a
named refusal — never a fabricated conclusion.

## In scope

- OpenAPI 3.1 documents, JSON or strict YAML (no aliases, merge keys,
  duplicate keys, or custom tags).
- FastAPI source discovered by `ast.parse` only: `FastAPI`/`APIRouter`
  decorators, literal paths and prefixes, `include_router` resolved across
  local imports, trailing-slash-sensitive route keys, duplicate routes
  retained.
- Canonical API-IR keyed by lowercase method + literal path, with zero, one,
  or many projections per side and full provenance.
- Bounded contract diff: removed/added operations and responses, required
  request-property and optional response-property deltas, local
  `#/components/schemas/...` refs only.
- Four executable divergence rules (`AF-CONTRACT-001`, `AF-CODE-001..003`)
  driven by the packaged catalog.
- Reproducible case persistence with hash-verified load.

## Explicitly out of scope

- **Executing analyzed code.** No import, no `eval`, no ASGI runtime.
- **Model calls.** The core never imports `openai`, `anthropic`, `boto3`,
  `litellm`, or any SDK; there is no LLM in the analysis path.
- **Network.** No `$ref` over HTTP, no telemetry, no update checks.
- **Framework inference beyond FastAPI.** Other frameworks are future
  adapters, not fallbacks.
- **Cloud access.** No credential probing, no provider calls.
- **Mutation.** Inputs are read-only; the only writes go to a validated
  `out_dir` that must not overlap inputs.

## Uncertainty contract

When extraction cannot prove something — a dynamic prefix, a parse failure,
an include cycle — the pipeline emits a named `unresolved` diagnostic naming
the blind spot. Rules that depend on the missing evidence downgrade to
`unresolved` rather than claim absence. Absence of evidence is not evidence
of absence.
