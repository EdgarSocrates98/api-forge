# DEFINE: API Forge Economy Hardening 3 — Eval, Policy and Governance Integrity

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_POLICY_INTEGRITY |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | [BRAINSTORM](./BRAINSTORM_API_FORGE_ECONOMY_POLICY_INTEGRITY.md) · `prompt_evo_new_economy_final.md` |
| **Branch** | `codex/economy-policy-integrity` |

---

## Problem Statement

The certification layer can still be misled by configuration: a baseline from
another corpus or with missing profiles counts as non-regression, an emptied
token-eligibility rule makes coverage fail open, and the GitHub ruleset that
should enforce checks and code owners targets no branch, lists no required
check, and relies on a CODEOWNERS file that does not exist.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Release guardian | Certifies economy changes | Baselines and coverage must not be fakeable by config |
| Repository owner | Owns GitHub governance | Declared governance is not materialized nor safely appliable |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | `BenchmarkIdentity/v1` in every `agentic-quality` report; baseline identity must match or be explicitly cross-corpus |
| **MUST** | Baseline requires `economy`, `balanced`, `deep` with accuracy in [0,1] |
| **MUST** | `token_eligibility.yaml` fails closed (schema, non-empty, no empty or duplicate prefix) |
| **MUST** | `.github/CODEOWNERS` committed and validated by a test |
| **MUST** | Read-only ruleset plan script: targets the default branch, adds the two required checks, preserves other rules, warns about rules that would block PR merges, never mutates |
| **SHOULD** | Docs: catalog, economy guide EN/PT-BR (program closure), governance guide EN/PT-BR, threat model EN/PT-BR |

---

## Success Criteria

- [ ] Report has `benchmark_identity` with `corpus_sha256`, `case_ids_sha256`, `case_count`, `profiles`, `claim_scope`, `evaluator_version`
- [ ] Baseline with different identity ⇒ `AF-EVALS-BASELINE-MISMATCH`; with `--allow-cross-corpus-baseline` ⇒ accepted, `baseline_scope: cross_corpus`
- [ ] Baseline without identity (legacy), missing a profile, or accuracy 1.5 ⇒ `AF-EVALS-BASELINE-INVALID`
- [ ] `verb_prefixes: []`, `[""]`, duplicates, wrong schema ⇒ `AF-ECONOMY-TOKEN-RULE-INVALID`
- [ ] provider A measured + provider B unmeasured ⇒ `partial` (never `complete`)
- [ ] CODEOWNERS test: file exists at `.github/CODEOWNERS`, every rule has an owner, every non-wildcard path exists
- [ ] Ruleset plan from the live JSON: `include: ["~DEFAULT_BRANCH"]`, required checks `Validate project` and `Validate API/Git/CI replay control plane`, other rules kept, warnings for `update`/`creation`, idempotent, output contains the `gh api -X PUT` command, no network call from the script
- [ ] Full suite and all economy evals pass

---

## Acceptance Tests

| ID | Scenario | Then |
|----|----------|------|
| AT-001 | Same corpus baseline | gates computed, `baseline_scope: same_corpus` |
| AT-002 | Different corpus baseline | refused `AF-EVALS-BASELINE-MISMATCH` |
| AT-003 | Different corpus + `--allow-cross-corpus-baseline` | accepted, `cross_corpus` recorded |
| AT-004 | Legacy/partial/out-of-range baseline | `AF-EVALS-BASELINE-INVALID` |
| AT-005 | Emptied/blank/duplicate/wrong-schema eligibility | `AF-ECONOMY-TOKEN-RULE-INVALID` |
| AT-006 | Measured + unmeasured provider rows | `partial` |
| AT-007 | CODEOWNERS | exists, owners present, paths exist |
| AT-008 | Ruleset plan on the current `protect` JSON | default-branch target, required checks, warnings, idempotent |
| AT-009 | Malformed ruleset JSON | `AF-GITHUB-RULESET-INVALID` |

---

## Out of Scope

- Applying the ruleset (user action); new economy features; identities for other evals.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Security | No remote mutation by the agent; `scripts/github_pr_host.py` stays the only GitHub mutation boundary | Plan script reads a JSON file/stdin only |
| Governance | AF code + field + unlock, cataloged | Release gate parity |
| Docs | Bilingual pairs | Governance guide EN + PT-BR |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/{contracts,evals,economy}`, `.github/CODEOWNERS`, `scripts/github_ruleset_plan.py`, `docs/` | |
| **KB Domains** | catalog, threat model, economy guide; agentspec python/testing/ci-cd | |
| **IaC Impact** | GitHub ruleset (plan only) | |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Ruleset `protect` (id 23971496) is active with an empty `ref_name.include` (targets no branch) | Plan target differs | [x] read-only `gh api` 2026-09-28 |
| A-002 | Ruleset has `update`, `creation`, `required_signatures`, `required_linear_history`, `non_fast_forward`, `deletion`, `pull_request` (code-owner review) and empty `required_status_checks`; no bypass actors | Plan warnings differ | [x] same read |
| A-003 | Required check names are the CI job names `Validate project` and `Validate API/Git/CI replay control plane` | Plan names wrong | [x] PR #15/#16 check runs |
| A-004 | Enforcing `update` on the default branch without bypass blocks PR merges | Warning wording | [ ] documented GitHub semantics; user verifies on apply |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Verified in code and live ruleset |
| Users | 3 | Two personas |
| Goals | 3 | MoSCoW |
| Success | 3 | Test-mapped |
| Scope | 2 | Final ruleset content is the user's decision at apply time |
| **Total** | **14/15** | |

---

## Open Questions

- User decision at apply time: keep `update`/`creation` restrictions on the default branch with an owner bypass, or drop them from the plan (`--drop-rule update`).

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial from BRAINSTORM + live ruleset read |

---

## Next Step

**Ready for:** `/agentspec:workflow:design .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_POLICY_INTEGRITY.md`
