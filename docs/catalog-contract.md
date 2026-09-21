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

## Detail level

`--detail-level` projects CLI payloads: `summary` drops verbose text keys
while refusal codes and `fact_id`s survive; `normal`/`full` are identical
today.

| Code | Meaning |
|---|---|
| `AF-DETAIL-LEVEL` | unknown detail level requested |
