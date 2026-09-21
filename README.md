# API Forge

Deterministic, offline, local-first API engineering. Given an existing FastAPI
project and an OpenAPI 3.1 contract, API Forge discovers routes, composes a
provenance-backed API-IR, judges contract/code divergence, classifies bounded
breaking changes, and persists a byte-reproducible evidence case.

> Resultado correto, verificável e reproduzível por token consumido.

## Install

```bash
python -m pip install -e '.[dev]'   # Python >=3.12,<3.13
```

## Analyze

```bash
apiforge analyze \
  --contract tests/fixtures/openapi/orders-v1.yaml \
  --project tests/fixtures/fastapi_orders \
  --out-dir .apiforge/case
```

Prints a compact JSON summary and writes a case directory:

| Artifact | Meaning |
|---|---|
| `api-ir.json` | Canonical API-IR: operations keyed by method+path, contract and code projections, provenance, input hashes, diagnostics |
| `facts.json` | Immutable evidence facts (code routes, contract operations) with source path/line/sha256 |
| `findings.json` | Rule verdicts — `confirmed` or `unresolved`, always evidence-backed |
| `changes.json` | Contract diff results — only when `--baseline` is given |
| `case.json` | Manifest written last; sha256 of every declared artifact |

Individual stages: `apiforge discover --project .`, `apiforge model build
--contract c.yaml --project .`, `apiforge diff contract --baseline a.yaml
--candidate b.yaml`, `apiforge judge --contract c.yaml --project .`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 2 | input/validation refusal (`AF-INPUT-NOT-FOUND`, `AF-OPENAPI-*`, `AF-CASE-*` storage) |
| 3 | integrity failure (`AF-CASE-HASH-MISMATCH`, ...) |
| 4 | confirmed finding at `--fail-on` severity or worse |

## Guarantees

- **No network.** No SDK, no model call, no `$ref` resolution over the wire.
- **No code execution.** FastAPI sources are parsed with `ast.parse`, never
  imported.
- **Read-only inputs.** Analyzed files are only read; `out_dir` overlapping an
  input is refused.
- **Reproducible.** Two runs on the same inputs produce byte-identical
  artifacts.

## Supported / unsupported

Supported: OpenAPI 3.1 (JSON or strict YAML — aliases, merge keys, duplicate
keys and custom tags rejected); FastAPI `FastAPI`/`APIRouter` decorators with
literal paths and `include_router`, including cross-file imports; local refs
`#/components/schemas/...` in the contract diff.

Unsupported (emits named `unresolved` diagnostics, never guesses): dynamic
route prefixes/paths, non-literal include targets, external or cyclic `$ref`,
arbitrary JSON Schema inference. See `docs/architecture/mvp-boundaries.md`.

## Verify a case

```bash
python -c "from apiforge.case.service import load_case; print(load_case('.apiforge/case').case_id)"
```

`load_case` re-hashes every declared artifact; tampering raises
`CaseIntegrityError` (`AF-CASE-HASH-MISMATCH`).

## Development

```bash
pytest -q
ruff check . && ruff format --check .
mypy src/apiforge
python scripts/check_mvp_release.py
```
