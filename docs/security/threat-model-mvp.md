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
| Fabricated conclusions | `unresolved` diagnostics and findings name the uncertainty; `confirmed` requires evidence fact_ids by construction |

## Known limitations

- The FastAPI extractor is static: routes registered by means other than
  decorators/`include_router` appear as `unresolved`, not routes.
- JSON Schema evaluation is bounded to the diff rules listed in the
  architecture boundary doc — arbitrary schema equivalence is not attempted.
- `load_case` verifies integrity (correspondence to the manifest), not
  authorship — there is no signing key.
