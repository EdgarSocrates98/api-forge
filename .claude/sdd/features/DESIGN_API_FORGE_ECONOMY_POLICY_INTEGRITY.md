# DESIGN: API Forge Economy Hardening 3 — Eval, Policy and Governance Integrity

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_POLICY_INTEGRITY |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_POLICY_INTEGRITY.md](./DEFINE_API_FORGE_ECONOMY_POLICY_INTEGRITY.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
P1 ─ benchmark + policy integrity
  evals/agentic_quality
    benchmark_identity(corpus) -> BenchmarkIdentity/v1
       corpus_sha256   = sha256 over (name + LF-normalized bytes) of sorted *.yaml
       case_ids_sha256 = sha256 of sorted case ids joined by "\n"
       case_count, profiles=("economy","balanced","deep"), claim_scope, evaluator_version
    load_baseline(path, identity, allow_cross) -> (accuracy, sha, scope)
       invalid (no identity / missing profile / out of [0,1]) -> AF-EVALS-BASELINE-INVALID
       identity differs and not allow_cross                   -> AF-EVALS-BASELINE-MISMATCH
       identity differs and allow_cross                       -> scope "cross_corpus"
  economy/run_ledger.eligible_prefixes (fail-closed)
       schema == apiforge/token-eligibility/v1, list non-empty, no blank, no duplicate
       else AF-ECONOMY-TOKEN-RULE-INVALID

P2 ─ governance (read-only)
  .github/CODEOWNERS (@EdgarSocrates98)
  scripts/github_ruleset_plan.py --input ruleset.json [--bypass-owner] [--drop-rule R] [--out plan.json]
       pure transform: target ~DEFAULT_BRANCH, required checks, keep rules, warnings,
       emits {payload, warnings, command, plan_sha256}; no subprocess, no network
```

---

## Key Decisions

### D1: BenchmarkIdentity/v1 contract

Registered contract with doc. `evaluator_version = f"agentic-quality/2+apiforge-{__version__}"`. Identity equality compares `corpus_sha256`, `case_ids_sha256`, `profiles` and `claim_scope` (evaluator version differences are reported, not refused — a new evaluator on the same corpus is still the same experiment; the report records both).

### D2: Strict baseline

Baseline must be `apiforge/agentic-quality-eval/v1` with `benchmark_identity` and `accuracy` covering exactly the three profiles, each a number in [0,1]. Legacy reports without identity are invalid (unlock: regenerate the baseline with the current evaluator). Report fields: `benchmark_identity`, `baseline_scope` (`same_corpus` | `cross_corpus` | null), `baseline_sha256`, `baseline_accuracy`. With `cross_corpus`, gates are named `<profile>_not_below_baseline_cross_corpus` so they cannot be mistaken for a same-experiment check. CLI/MCP: `--allow-cross-corpus-baseline`.

### D3: Fail-closed eligibility

`eligible_prefixes` validates schema, non-empty list, no blank/whitespace prefix, no duplicates. `stats` surfaces the refusal (no partial fallback) — a broken policy can never report `complete`.

### D4: CODEOWNERS

```
*                        @EdgarSocrates98
/src/apiforge/security/  @EdgarSocrates98
/src/apiforge/economy/   @EdgarSocrates98
/.github/                @EdgarSocrates98
/.github/CODEOWNERS      @EdgarSocrates98
```
Test parses it: each non-comment line has a pattern and ≥1 `@owner`; non-wildcard paths exist.

### D5: Read-only ruleset plan

Outside `src/` like `github_pr_host.py`. Input is the ruleset JSON (from `gh api repos/<o>/<r>/rulesets/<id>`), never fetched by the script. Transform:
- `conditions.ref_name.include = ["~DEFAULT_BRANCH"]` when empty (warning if it was empty: "ruleset targets no branch today");
- `required_status_checks.required_status_checks = [{"context": "Validate project"}, {"context": "Validate API/Git/CI replay control plane"}]`, `strict_required_status_checks_policy = true`;
- `--bypass-owner` adds `{"actor_type": "RepositoryRole", "actor_id": 5, "bypass_mode": "pull_request"}` (repository admin role);
- `--drop-rule` removes named rule types;
- warnings for kept `update` (blocks PR merges without bypass), `creation`, `required_signatures`;
- output keeps only PUT-able keys (`name`, `target`, `enforcement`, `conditions`, `rules`, `bypass_actors`), is idempotent, adds `command` (`gh api -X PUT repos/{repo}/rulesets/{id} --input plan-payload.json`) and `plan_sha256`.
Malformed input → exit 2 with `AF-GITHUB-RULESET-INVALID (field=...; unlock=...)`.

---

## File Manifest

| # | File | Action | Wave |
|---|------|--------|------|
| 1 | `src/apiforge/contracts/economy_evals.py` (+ registry, doc) | `BenchmarkIdentity/v1` | P1 |
| 2 | `src/apiforge/evals/agentic_quality.py`, `cli.py`, `mcp/tools.py` | identity, strict baseline, flag | P1 |
| 3 | `src/apiforge/economy/run_ledger.py` | fail-closed parser | P1 |
| 4 | `tests/economy/test_policy_integrity.py` | mutation tests | P1 |
| 5 | `.github/CODEOWNERS`, `tests/test_codeowners.py` | owners + test | P2 |
| 6 | `scripts/github_ruleset_plan.py`, `tests/test_github_ruleset_plan.py`, `tests/fixtures/github/ruleset_protect.json` | plan + tests | P2 |
| 7 | `docs/guides/API_FORGE_GITHUB_GOVERNANCE.md` + `.en.md`, catalog, threat model EN/PT-BR, economy guide EN/PT-BR, README rows, SDD chain | docs | P1/P2 |

---

## Testing Strategy

| Test | Proves |
|------|--------|
| identity stable across runs; changes when a case file changes | D1 |
| mismatched baseline refused; allowed with flag and recorded; legacy/partial/1.5 invalid | D2 |
| `[]`, `[""]`, `["  "]`, duplicates, wrong schema → refusal; measured+unmeasured provider → partial | D3 |
| CODEOWNERS parse | D4 |
| plan on the live `protect` JSON fixture: include default branch, checks, warnings, idempotent, bypass/drop flags, malformed refusal, script has no subprocess/network import | D5 |

---

## Error Handling

| Code | When |
|------|------|
| `AF-EVALS-BASELINE-MISMATCH` | baseline benchmark identity differs without `--allow-cross-corpus-baseline` |
| `AF-EVALS-BASELINE-INVALID` | legacy/partial/out-of-range baseline |
| `AF-ECONOMY-TOKEN-RULE-INVALID` | eligibility rule fails validation |
| `AF-GITHUB-RULESET-INVALID` | ruleset JSON malformed |

---

## Next Step

**Ready for:** `/agentspec:workflow:build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_POLICY_INTEGRITY.md`
