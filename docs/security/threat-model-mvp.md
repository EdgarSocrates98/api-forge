# Threat model — MVP

API Forge parses potentially hostile inputs: a contract and a source tree the
operator did not write. The analysis path executes no input code and touches
no network, which removes the largest classes; the remaining ones are listed
with their mitigations.

| Threat | Mitigation |
|---|---|
| Malicious YAML/JSON (billion laughs, custom tags, unsafe constructors) | Strict loader: aliases and merge keys rejected at the event level, custom tags refused, `SafeConstructor` only, implicit resolvers restricted to JSON-compatible scalars, duplicate keys and non-finite numbers rejected |
| Hostile source code | `ast.parse` only — the analyzed module is never imported or executed; decorators are matched by name, not evaluated |
| Path traversal in `out_dir` | `..` components refused (`AF-CASE-PATH-TRAVERSAL`); declared artifact paths in `case.json` re-checked on load |
| Symlink escapes | `out_dir` ancestor chain checked for symlinks (`AF-CASE-SYMLINK`); the extractor does not follow symlinks outside the project root |
| Input/output overlap | `out_dir` containing or contained by a contract/project input is refused (`AF-CASE-INPUT-OUTPUT-OVERLAP`) — inputs stay read-only |
| Secret leakage | Artifacts contain paths, hashes, and AST-extracted literals only; no environment variables, no file contents beyond parsed route metadata are emitted |
| Resource exhaustion | YAML event stream rejected construct-by-construct; extraction is a bounded two-pass AST walk; no recursion into unbounded external refs (only `#/components/schemas`, cycle-detected) |
| Tampered case artifacts | `load_case` re-hashes every declared artifact (`AF-CASE-HASH-MISMATCH`); manifest is written last so it never references a missing artifact |
| Policy tampering | the policy catalog is closed-schema data (`AF-POLICY-SCHEMA`); every release receipt pins `policy_sha256`, so a tampered catalog no longer matches any prior receipt |
| Crafted diff path escape | sandbox patch paths are validated against the copied root before any byte is written (`AF-SANDBOX-PATH-OUTSIDE`); binary and mode-only diffs are refused outright |
| Symlinks inside copied trees | the sandbox inventory skips symlinks and copies with `follow_symlinks=False`, so a patch can never write through a link out of the copy |
| Frontmatter injection | SDD frontmatter uses the strict YAML loader (no aliases, tags or duplicate keys); `stamp` rewrites only the upstream hash line |
| Gate override abuse | a strict `set-phase` bypass is never silent: `gate`, `reason` and `actor` are recorded in `gate-overrides.json` under `.apiforge/sdd/<FEATURE>/` |
| Worktree index drift/confusion | `worktree_list` reconciles `index.json` against `git worktree list --porcelain` and reports drift in both directions instead of hiding it |
| Malformed Java source (tree-sitter) | the parser never executes code and cannot call the target toolchain; parse errors degrade to `AF-SPRING-PARSE` diagnostics with the file still hashed, and non-literal annotation args become `AF-SPRING-UNRESOLVED-ROUTE` |
| Malformed Go source (tree-sitter) | identical boundary: no toolchain contact, no code execution; parse errors degrade to `AF-GO-PARSE` and dynamic registrations to `AF-GO-UNRESOLVED-ROUTE` |
| AWS credential/network abuse | only `collect *` imports boto3 (release-gate enforced); `analyze`/`model` verbs read dumps offline and never see credentials; dumps land under an explicit `--out` dir with `*.json`-only artifact names |
| Secret leakage via collected dumps | `collect lambda` drops `Code.Location` (pre-signed URL) before writing; `model lambda`/`model terraform` extract env var **names** only — values are never read into facts |
| Template intrinsic injection | SAM `!Ref`/`!Sub`/`!GetAtt` tags construct only `{tag, value}` data under a `SafeLoader` subclass — no objects, no resolution; tagged properties are `AF-SAM-UNRESOLVED`. Terraform `${...}` interpolations are `AF-TF-UNRESOLVED`, never evaluated |
| Generated-code escape | `build` emits new files only under `com/apiforge/generated/`, refuses existing targets, evaluates via `sandbox_apply` (which itself refuses path escapes), and promotion writes solely inside a policy-gated git worktree |
| Agent profile drift | coordinator/executor `.md` profiles are prose contracts, not enforcement — the gate re-checks them: frontmatter `name` == filename, `rule_areas` ⊆ catalog, `executors` exist as files, every routing `recommended_agent` has a profile and a playbook, and every profile references `AGENT_PROTOCOL.md` |
| Economy ledger forgery | the ledger is append-only local JSONL measuring emitted bytes; `economy report` recomputes aggregates from the file, reports `tokens_unresolved` without a transcript, and never attributes tokens or dollars that were not measured |
| Secret exfiltration via reports | the gitleaks reader emits rule/file/count only — secret values and match text are never extracted; test asserted |
| Report forgery | `report verify` re-hashes body/evidence/catalog and names each diverged part; the signature binds hashes, not identity — correspondence, never authorship (ADR-005) |
| External tool execution | `run tool` executes only the allowlisted binaries (semgrep/trivy/gitleaks/k6) via fixed argv templates — no shell, `shutil.which` resolution, `--timeout` bound; the analyzed code is still never executed (the scanner runs, the target stays data), and `--dry-run` shows the argv beforehand |
| Fabricated conclusions | `unresolved` diagnostics and findings name the uncertainty; `confirmed` requires evidence fact_ids by construction |
| Tampered task spec/history | the Ed25519 seal binds the exact revision bytes — amending a sealed task writes a new unsealed revision, so a stale seal can never ride along; `history.jsonl` is append-only and `task accept` requires `accepted_by != executed_by` plus named evidence |
| Stale extractor cache poisoning | cache keys are `sha256(extractor_version|framework|source_digest)` — a changed file yields a new key (stale entries are unreachable, never wrong); a corrupt or schema-invalid cache file self-heals as a miss and is rewritten; the extractor stays the source of truth |
| Graph line tampering | every `nodes.jsonl` line carries a `sha256` over its `{id,kind,props}` payload — load refuses `AF-GRAPH-HASH-MISMATCH`; files are sorted canonically so byte drift is diff-visible |
| False `DONE` claim | `brief show` derives status from the task state machine — `DONE` exists only after `awaiting_supervision -> accepted` by a distinct actor with evidence; gaps, pending human action and open items are fields, not prose |

## Known limitations

- The FastAPI extractor is static: routes registered by means other than
  decorators/`include_router` appear as `unresolved`, not routes.
- JSON Schema evaluation is bounded to the diff rules listed in the
  architecture boundary doc — arbitrary schema equivalence is not attempted.
- `load_case` verifies integrity (correspondence to the manifest), not
  authorship — there is no signing key.
