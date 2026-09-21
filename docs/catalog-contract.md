# Catalog, routing and adapter contract

## Rule catalog

`src/apiforge/rules/catalog/*.yaml` — one file per area, merged in sorted
order by `load_catalog()`. File schema: `catalog_version`, `schema_version`,
`area` (required), `retrieved`, `rules[]`. Rule keys are closed:
`id`, `title`, `severity`, `rationale`, `remediation`, `reference`,
`runtime_scope`. `expected_gain` is refused by schema — asserting a saving
requires the cost of the run that never happened.

| Code | Meaning |
|---|---|
| `AF-CATALOG-SCHEMA` | rule/file violates the closed schema (unknown key, `expected_gain`, missing field) |
| `AF-CATALOG-INVALID` | catalog file fails strict YAML parsing |
| `AF-CATALOG-AREA-MISSING` | catalog file lacks the required `area` header |
| `AF-CATALOG-DUPLICATE-RULE` | the same rule id appears in two files |

## Routing

`catalog/routing.yaml` maps `(phase, dominant_area)` → `recommended_agent`;
phases are the canonical SDD vocabulary, areas come from the catalog itself.
`next-step` composes over findings — ties between areas break by highest
severity then area name; unmapped rule_ids are counted, never routed.

| Code | Meaning |
|---|---|
| `AF-ROUTING-SCHEMA` | `routing.yaml` malformed |
| `AF-ROUTING-CATALOG` | the rule catalog failed to load while routing |
| `AF-ROUTING-NO-FINDINGS` | `next-step` invoked with an empty finding list |
| `AF-ROUTING-NO-ROUTE` | no route covers the (phase, dominant_area) pair — refusal, never a guess |

## Spring adapter

`extract_spring` parses `*.java` with tree-sitter — no JDK, no build tool, no
code execution. Non-literal annotation arguments and unresolvable route
shapes are named diagnostics, never inferred.

| Code | Meaning |
|---|---|
| `AF-SPRING-UNRESOLVED-ROUTE` | annotation argument is not a string literal (constant, SpEL, composed meta-annotation) |
| `AF-SPRING-PARSE` | tree-sitter reported a parse error; the file is hashed and extraction is partial |

## Go adapter

`extract_go` parses `*.go` with tree-sitter — no `go` toolchain, no module
resolution, no code execution. Recognized shapes: chi/net-http/gin/echo
verb calls, `mux.Handle`/`HandleFunc` (Go 1.22 `"METHOD /path"` patterns;
bare paths record method `any`), `Route`/`Group` scope joins. `Mount`,
middleware (`Use`, `With`, `Method`) and non-literal paths are named
diagnostics, never inferred.

| Code | Meaning |
|---|---|
| `AF-GO-UNRESOLVED-ROUTE` | route shape could not be resolved statically (non-literal path, `Mount`, middleware) |
| `AF-GO-PARSE` | tree-sitter reported a parse error; the file is hashed and extraction is partial |

## Detail level

`--detail-level` projects CLI payloads: `summary` drops verbose text keys
while refusal codes and `fact_id`s survive; `normal`/`full` are identical
today.

| Code | Meaning |
|---|---|
| `AF-DETAIL-LEVEL` | unknown detail level requested |

## AWS collectors

`collect *` is the only verb family that touches AWS; boto3 imports are
confined to `apiforge.collectors` and enforced by the release gate. Dumps
are canonical JSON + a `manifest.json` receipt; `--now` is the only clock.

| Code | Meaning |
|---|---|
| `AF-COLLECT-AWS` | the AWS call failed; the named operation is in the detail |
| `AF-COLLECT-PATH` | artifact name refused (not a plain `*.json` basename) |

## API Gateway dump adapter

`model api-gateway --path` reads a collect dump offline. Missing files and
malformed JSON are named diagnostics, never guesses.

| Code | Meaning |
|---|---|
| `AF-GW-DUMP-MISSING` | an expected dump file is absent |
| `AF-GW-DUMP-INVALID` | a dump file is not valid JSON |

## Builder

`build endpoint` synthesizes Spring skeletons as new-file unified diffs,
evaluates them in the copy sandbox, and promotes into a git worktree only
when the `sensitive`-class gates (`evidence`, `approval`) are satisfied.
It never edits existing files and never writes to the main tree.

| Code | Meaning |
|---|---|
| `AF-BUILD-OP-MISSING` | the requested operationId (or method) is absent from the contract |
| `AF-BUILD-SCHEMA-MISSING` | a schema node has no bounded Java mapping — refused, never guessed |
| `AF-BUILD-TARGET-EXISTS` | a generated path already exists — builds never clobber |

## Agentic layer

`apiforge playbook <coordinator>` renders the executor decomposition declared
in `playbooks.yaml` — the floor on platforms that cannot dispatch subagents.
Coordinator names equal `agents/*.md` profiles; every `recommended_agent` in
`routing.yaml` must have both a profile and a playbook (release-gated).

The economy ledger appends `{verb, detail_level, payload_bytes}` per emitted
payload to `.apiforge/economy.jsonl`; `economy report` aggregates and shows
`detail_level_effect`. Tokens are `tokens_unresolved` without a provider
transcript — measured bytes only, never invented numbers.

| Code | Meaning |
|---|---|
| `AF-PLAYBOOK-NOT-FOUND` | no playbook for the named coordinator; known names are in the detail |
