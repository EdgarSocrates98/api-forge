# SDD contract

API Forge develops itself through specification-driven development. A feature
is a directory `docs/sdd/<FEATURE>/` holding one Markdown file per phase; each
file carries strict YAML frontmatter (`sdd: 1`) and links to its upstream
artifact by content hash — the hash cascade.

## Phases (canonical order)

`discover → intent → contract → architecture → plan → build → verify →
secure → benchmark → ship`

Profiles select a subset of phases; `profiles.yaml` (package data) defines
`quick`, `standard`, `critical` and `migration`. A phase a profile does not
require may still be present; a required phase that is skipped must be marked
`status: not_required` with a `justification` field.

## Frontmatter

Every artifact: `sdd: 1`, `feature` (must equal the directory name), `phase`
(must equal the file stem), `profile`, `status` in
`draft|ready|done|superseded|not_required`. Every phase except `discover`
declares `upstream: {path, sha256}` pointing at the artifact it builds on;
`sdd stamp` rewrites only that hash line and never touches other bytes.

Per-phase required fields: `discover`: `approaches`, `chosen`; `intent`:
`problem`, `success[]`, `out_of_scope`; `contract`: `covers`, optional
`api_ir`; `architecture`: `files`, `decisions[]` each with `rollback`;
`plan`: `tasks[]` each with `covers` and `test` or `proof`; `build`:
`tasks[].status`, `claims`; `verify`: `results`; `secure`: `threat_model`;
`benchmark`: `baseline`, `results`; `ship`: `deviations`, `evidence[]` of
`{path, sha256}`.

## Gates

`gates.yaml` maps a gate to `{satisfied_by, produced_by, guards_phases}`.
Under `sdd set-phase --strict`, entering a guarded phase at `ready`/`done`
requires the named evidence kind to exist as `<evidence_dir>/<kind>.json`.
Evidence presence unlocks — never a boolean flag. When evidence genuinely
cannot exist, `--override-gate/--override-reason/--override-actor` records the
bypass in `.apiforge/sdd/<FEATURE>/gate-overrides.json`.

Known evidence kinds: `contract.document`, `plan.tasks`, `test.results`,
`threat.model`, `benchmark.results`, `release.receipt`.

Extraction is deliberately narrow. `test.results` reads only the pytest
tally line (`N passed[, N failed][, N skipped][, N error]`) — output from
another harness (JUnit XML, `go test`, TAP) is *not* parsed and refuses
with `AF-SDD-EVIDENCE-EXTRACT`. Unsupported formats stay unresolved;
the extractor never interpolates or invents counts.

## Refusal and gap codes

Refusals (`refused[]`) block `ok`; named gaps (`unresolved[]`) are reported at
`ready` and block `done` and `--strict` runs.

| Code | Meaning |
|---|---|
| `AF-SDD-SCHEMA-INVALID` | frontmatter violates the schema (status, version, required field) |
| `AF-SDD-FRONTMATTER` | artifact frontmatter fails to parse or is absent |
| `AF-SDD-PHASE-ORDER` | `upstream.path` does not point to an earlier phase |
| `AF-SDD-UPSTREAM-MISSING` | upstream declaration absent or file missing |
| `AF-SDD-UPSTREAM-STALE` | upstream content changed since the hash was stamped |
| `AF-SDD-ACCEPTANCE-UNCOVERED` | an `intent.success` item is covered by no plan task |
| `AF-SDD-TASK-WITHOUT-TEST` | a plan task has neither `test` nor `proof` |
| `AF-SDD-PHASE-SKIPPED-UNDECLARED` | a required phase is absent or lacks `not_required`+`justification` |
| `AF-SDD-EVIDENCE-MISMATCH` | a `ship.evidence` hash diverges from the file |
| `AF-SDD-GAP-TEST-NOT-WRITTEN` | declared test file does not exist |
| `AF-SDD-GAP-FACT-NOT-COLLECTED` | a build claim references evidence not produced |
| `AF-SDD-GAP-FINDING-NOT-OBSERVED` | a verify result references a finding never observed |
| `AF-SDD-GATE-BLOCKED` | strict transition refused: gate evidence absent and no override |
| `AF-SDD-EVIDENCE-KIND` | `sdd evidence --kind` satisfies no gate in `gates.yaml` |
| `AF-SDD-EVIDENCE-SOURCE` | `sdd evidence --from` names no file |
| `AF-SDD-EVIDENCE-EXTRACT` | the kind's extractor cannot read the source (e.g. no pytest tally) |
| `AF-SDD-ARTIFACT-MISSING` | `set-phase` target file absent |
| `AF-SDD-NOT-FOUND` | `--feature` names no directory under the SDD root |
| `AF-SDD-FEATURE-UNKNOWN` | `--feature` names a directory that does not exist |
| `AF-SDD-UNKNOWN-FILE` | a `.md` file whose stem is not a canonical phase |
| `AF-SDD-PROFILES` | `profiles.yaml` malformed or missing a required profile |
| `AF-SDD-GATES` | `gates.yaml` malformed |
| `AF-SDD-STAMP` | stamping failed (frontmatter/upstream field invalid) |
