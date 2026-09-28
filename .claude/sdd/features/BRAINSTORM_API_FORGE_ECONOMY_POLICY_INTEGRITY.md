# BRAINSTORM: API Forge Economy Hardening 3 — Eval, Policy and Governance Integrity

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_POLICY_INTEGRITY |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |
| **Source** | `prompt_evo_new_economy_final.md` (review of `main` @ `333b706`, verdict `PASS — ECONOMY ARCHITECTURE HARDENED`) |
| **Branch** | `codex/economy-policy-integrity` |

---

## Initial Idea

**Raw Input:** The reviewer approved the economy architecture and asks for a
small closing "Hardening 3": make baselines prove they measure the same
benchmark, make the token-eligibility policy fail closed, and back the CI
narrative with GitHub enforcement (required checks + CODEOWNERS). After this
the economy program closes.

**Context Gathered (verified in code):**
- `evals/agentic_quality.load_baseline` checks schema and float accuracy only; no corpus identity, partial profile sets accepted.
- `economy/run_ledger.eligible_prefixes` accepts `verb_prefixes: []`, `[""]` and any `schema` — an empty rule makes unmeasured provider rows ineligible (fail-open coverage).
- Ruleset `protect` has `require_code_owner_review = true` but no CODEOWNERS file exists, and `required_status_checks` is empty (per reviewer; re-read at build).
- `scripts/github_pr_host.py` is the only GitHub mutation boundary (CLAUDE.md).

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/evals/agentic_quality.py`, `src/apiforge/contracts/`, `src/apiforge/economy/run_ledger.py`, `.github/CODEOWNERS`, `scripts/` | Small diffs + one contract + one read-only script |
| Relevant KB Domains | repo: catalog, threat model EN/PT-BR, economy guide EN/PT-BR, `scripts/github_pr_host.py`; agentspec: python, testing, ci-cd | Governance stays user-applied |
| IaC Patterns | GitHub rulesets (remote config) | Plan only, never applied by the agent |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | GitHub governance: how? | CODEOWNERS in repo + read-only ruleset plan script and guide; user applies | No remote mutation by the agent |
| 2 | CODEOWNERS activates code-owner review with a single maintainer | Create CODEOWNERS + ruleset plan with an optional owner bypass | Documented trade-off; auto-merge not silently blocked |
| 3 | Baseline from another corpus? | Refuse (`AF-EVALS-BASELINE-MISMATCH`) unless `--allow-cross-corpus-baseline`, recorded as `cross_corpus` | Baseline = previous measurement of the same experiment |
| 4 | Samples / ground truth? | Prompt scenarios as mutation tests | Each fix proven by a failing-before test |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `evals/corpus/agentic-quality/`, `src/apiforge/rules/token_eligibility.yaml` | 6 cases + 1 rule | Identity computed over the corpus |
| Output examples | `docs/sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/agentic-quality-eval.json` | 1 | Pre-identity report (must be refused as baseline) |
| Ground truth | Prompt §10–13 scenarios | 8 | Mutation tests |
| Related code | `scripts/github_pr_host.py`, `.github/workflows/ci.yml` | — | Job names for required checks |

---

## Approaches Explored

### Approach A: Small fail-closed closure ⭐ Recommended

**What:** `BenchmarkIdentity/v1` + strict baseline validation; fail-closed eligibility parser with mutation tests; `.github/CODEOWNERS`; read-only `scripts/github_ruleset_plan.py` producing the ruleset payload and the `gh api` command for the user.
**Pros:** small diff; every fix test-backed; remote governance under user control.
**Cons:** ruleset enforcement only after the user applies it.
**Why Recommended:** matches the repo's single-mutation-boundary rule (CLAUDE.md) — confidence 0.95.

### Approach B: Agent applies the ruleset via `gh api`

**Pros:** complete in one step. **Cons:** administrative remote mutation outside the mutation boundary.
**Why not:** user chose to apply it.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28, explicit choice in session |
| **Reasoning** | Fail-closed certification with governance the user applies |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | `BenchmarkIdentity/v1` in every agentic-quality report | A baseline must measure the same experiment | number-only baseline |
| 2 | Baseline requires all 3 profiles, accuracies in [0,1] and matching identity | Partial/foreign baselines are not regression checks | partial acceptance |
| 3 | Cross-corpus only with explicit flag, recorded in the report | Deliberate exceptions stay visible | silent comparison |
| 4 | Eligibility rule fails closed (schema, non-empty, no empty/duplicate prefixes) | Never declare complete measurement without proof | lenient parser |
| 5 | CODEOWNERS committed; ruleset plan is read-only | User applies remote governance | agent mutates ruleset |
| 6 | Owner bypass optional in the plan, trade-off documented | Single maintainer must not deadlock auto-merge | forced bypass or none |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Economy Wave 9 | Reviewer: architecture is mature; avoid "spending complexity to save complexity" | Only on evidence |
| Applying the ruleset from the agent | User applies; single mutation boundary | Yes |
| Identity for the other economy evals | Only agentic-quality has baselines | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| P1: BenchmarkIdentity + fail-closed eligibility | ✅ | Approved | No |
| P2: CODEOWNERS + read-only ruleset plan | ✅ | Approved | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
The certification layer can still be misled by configuration: a baseline from
another corpus or with missing profiles counts as non-regression, an emptied
eligibility rule makes coverage fail open, and GitHub enforces neither
required checks nor the code-owner rule it declares.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Release guardian | Baselines and coverage must be impossible to fake by config |
| Repository owner | Governance intent (code owners, required checks) is not materialized |

### Success Criteria (Draft)
- [ ] Report carries `benchmark_identity`; mismatched baseline refused unless `--allow-cross-corpus-baseline`
- [ ] Baseline missing a profile or with accuracy outside [0,1] refused
- [ ] `verb_prefixes: []`, `[""]`, wrong schema, duplicates ⇒ `AF-ECONOMY-TOKEN-RULE-INVALID`
- [ ] provider A measured + provider B unmeasured ⇒ `partial`
- [ ] `.github/CODEOWNERS` exists, validated by test
- [ ] Ruleset plan adds the two required checks, preserves other rules, is idempotent, never mutates
- [ ] Full suite and all economy evals pass

### Constraints Identified
- No remote mutation by the agent; AF code + field + unlock, cataloged; bilingual docs.

### Out of Scope (Confirmed)
- New economy features; applying the ruleset.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 4 |
| Approaches Explored | 2 |
| Features Removed (YAGNI) | 3 |
| Validations Completed | 2 |
| Duration | 1 session |

---

## Next Step

**Ready for:** `/agentspec:workflow:define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_POLICY_INTEGRITY.md`
