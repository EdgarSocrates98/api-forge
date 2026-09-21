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

Frameworks: `analyze --framework fastapi|spring|go|auto` — `auto` counts
`.java`/`.py`/`.go` files (none → `AF-INPUT-FRAMEWORK-UNKNOWN`). The Spring adapter
parses `*.java` with tree-sitter (`@RestController`/`@RequestMapping`/
`@GetMapping`…, `RouterFunctions.route`, JAX-RS); non-literal annotation args
emit `AF-SPRING-UNRESOLVED-ROUTE`, never inference. The Go adapter covers
chi (`Route` scopes, verb calls), `net/http` (`Handle`/`HandleFunc` with Go
1.22 `"METHOD /path"` patterns) and gin/echo verb calls; `Mount`, middleware
and non-literal paths emit `AF-GO-UNRESOLVED-ROUTE`. Every JSON command accepts
`--detail-level summary|normal|full`; `summary` drops verbose text fields
while refusal codes and `fact_id`s survive.

## Governance

| Command | Purpose |
|---|---|
| `apiforge policy check --verb fs.delete --class destructive` | Evaluate an action against the policy catalog (allow/gate/deny) |
| `apiforge sdd check --root docs/sdd [--strict]` | Validate phase frontmatter, upstream hash cascade and evidence gates |
| `apiforge sdd status --root docs/sdd` | Per-feature phase status summary |
| `apiforge sdd stamp --artifact f/plan.md --upstream f/contract.md` | Write the upstream sha256 into frontmatter (line surgery only) |
| `apiforge sdd set-phase --root R --feature F --phase P --status S [--strict]` | Transition a phase; gates need evidence or a recorded override |
| `apiforge sandbox apply --root . --diff change.diff` | Apply a diff to copied before/after trees and report the finding delta |
| `apiforge sandbox clean --root .` | Remove `.apiforge/sandbox` only |
| `apiforge evidence emit --case .apiforge/case --out receipt.json` | Receipt binding artifact paths to sha256 (proves correspondence, not authorship) |
| `apiforge evidence verify --receipt receipt.json` | Re-hash every artifact the receipt lists |
| `apiforge next-step --findings findings.json --phase verify` | Route the dominant finding area to the specialist agent |
| `apiforge rules list [--area SECURITY]` | List catalog rules — the knowledge base every finding cites |
| `apiforge rules lookup AF-SEC-001` | Print one rule's rationale/remediation/reference |
| `apiforge collect api-gateway --api-id X --out dump/` | Fetch API Gateway config into an offline dump (needs `pip install apiforge[aws]`; the only family that touches AWS) |
| `apiforge model api-gateway --path dump/` | Read the dump into facts — offline, no credentials |
| `apiforge build endpoint --contract c.yaml --operation-id X --project .` | Synthesize a Spring skeleton, prove it in the sandbox (main tree untouched) |
| `apiforge build endpoint ... --into-worktree NAME --approve` | Promote generated files into a policy-gated git worktree |
| `apiforge playbook api-governance-reviewer` | Render the coordinator's executor decomposition — works without dispatch |
| `apiforge economy report [--root .]` | Measured call sizes; `detail_level_effect` shows what `summary` saves |
| `apiforge context funnel --case .apiforge/case` | Measured bytes per case stage (api-ir → facts → findings → summary) |
| `apiforge-mcp` | MCP server for the read/compose verbs (needs `pip install apiforge[mcp]`; every tool takes `detail_level`) |
| `apiforge collect lambda --function-name X --out dump/` | Fetch Lambda config into a dump (Code.Location never persisted) |
| `apiforge model lambda --path dump/` | Lambda facts offline — env var names only, values never read |
| `apiforge model terraform --path infra/` | API Gateway + Lambda resources from HCL; `${...}` → `AF-TF-UNRESOLVED` |
| `apiforge model sam --path template.yaml` | Serverless resources; `!Ref`/`!Sub` → `AF-SAM-UNRESOLVED` |
| `apiforge model pact\|schemathesis\|k6\|coverage --path r.json` | Test-tool reports → `test.*` facts (tools never run) |
| `apiforge model zap\|semgrep\|trivy\|gitleaks --path r.json` | Security reports → `sec.*` facts (gitleaks never emits secrets) |
| `apiforge report build --case .apiforge/case --out report.json` | Compose the release evidence bundle |
| `apiforge report sign --report report.json` | Pin body/evidence/catalog hashes into the signature block |
| `apiforge report verify --report report.json` | Name the diverged part (body\|evidence\|catalog\|signature_version); exit 4 |

## Agentic layer

Ten coordinator profiles in `agents/*.md` (one per specialty, each declaring
`rule_areas` and the five executors) plus five executors in
`agents/executors/*.md` (`af-inventory`, `af-extractor`, `af-judge`,
`af-verifier`, `af-synthesizer`). `AGENT_PROTOCOL.md` is the operating
contract every profile points at; `next-step` routes by data, `playbook`
is the dispatch floor, and `.apiforge/economy.jsonl` measures every call.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 2 | input/validation refusal (`AF-INPUT-NOT-FOUND`, `AF-OPENAPI-*`, `AF-CASE-*` storage) |
| 3 | integrity failure or denied/blocked governance result (`AF-CASE-HASH-MISMATCH`, `AF-POLICY-DENY`, `sdd check` not ok, ...) |
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
python scripts/check_release.py
```
