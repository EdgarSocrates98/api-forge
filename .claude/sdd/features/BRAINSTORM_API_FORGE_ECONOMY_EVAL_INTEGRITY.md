# BRAINSTORM: API Forge Economy Hardening 2 — Eval Integrity

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EVAL_INTEGRITY |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |
| **Source** | `prompt_evo_new_economy.md` (review of `main` @ `6d2f263`, verdict `PASS COM FOLLOW-UPS`) |
| **Branch** | `codex/economy-eval-integrity` |

---

## Initial Idea

**Raw Input:** The reviewer closed every P1/P2 of the previous round and now
asks for a small "Economy Hardening 2 / Eval Integrity": the layer that
*measures and certifies* the economy must be as rigorous as what it measures.

**Context Gathered (verified in code):**
- `evals/agentic_quality.py` gates are only relative (`economy >= deep`, `balanced >= deep`) plus answered/not blocked: all profiles at 0% accuracy still pass.
- `economy/run_ledger.py::token_coverage` treats every attribution row as eligible, so deterministic rows (capsule) make fully measured model calls look `partial`.
- `run_ledger.persist_failures(root)` counts the whole marker file; `stats --run-id B` inherits run A's failure.
- `evals/hardening.py` recomputes class-pool arithmetic and calls `_runtime_path` instead of `plan_roles`/`build_delta` — the oracle duplicates the logic it should guard.
- `context/delta.py` keeps absolute `--changed` paths and reads them for symbol mentions; `--case-dir`/`--case` are not confined.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/{evals,economy,context,evidence}`, `src/apiforge/rules/` | Small, localized diffs |
| Relevant KB Domains | repo: catalog contract, threat model EN/PT-BR, economy guide EN/PT-BR; agentspec: python, testing | Docs move with code |
| IaC Patterns | N/A | — |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | How to define the agentic-quality absolute floor? | Fixed floor `--min-accuracy` (default 1.0) + optional recorded `--baseline` | Gates: per-profile floor, not-below-deep, not-below-baseline |
| 2 | Which ledger rows are token-eligible? | Declarative rule by verb/source (`rules/token_eligibility.yaml`); rows with measured tokens always eligible | `is_token_eligible(row)`; deterministic rows leave the denominator |
| 3 | Explicit `context delta` paths? | Option A: `--changed`, `--case-dir`, `--case` pass through AllowedRoots | Out-of-root `--changed` item unresolved; out-of-root case dir refused |
| 4 | Samples / ground truth? | Prompt scenarios + fixtures | All-wrong corpus ⇒ fail; mixed ledger ⇒ complete 1500; run-A/B isolation; real delta on `economy_payments` |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/economy_payments/` | 1 fixture | Real `plan_roles`/`build_delta` in the hardening eval |
| Output examples | `evals/corpus/agentic-quality/`, `evals/corpus/economy-hardening/` | 6 + 15 cases | Extended, not replaced |
| Ground truth | Prompt §11–15 scenarios | 5 | Become mutation-style tests |
| Related code | `security/source_paths.py`, `runtime/role_context.py`, `context/delta.py` | — | Reused primitives |

---

## Approaches Explored

### Approach A: Targeted fixes with mutation tests ⭐ Recommended

**What:** Floor + baseline gates in `agentic-quality`; declarative token eligibility; run-scoped persist failures; hardening eval on production paths; explicit delta/case paths through AllowedRoots.

**Pros:** small localized diff; every fix has a test that fails on the old bug.
**Cons:** evals keep individual harnesses.
**Why Recommended:** the reviewer asks for a small hardening, not a wave; precedent: absolute envelope gate added to selective-agentics (confidence 0.95).

### Approach B: Common eval-oracle framework

**What:** shared base forcing every eval to use production paths and floors/baselines.
**Pros:** enforces "never reimplement the oracle" everywhere.
**Cons:** refactors 10 evals, regression risk, beyond requested scope.
**Why not:** exactly the large wave the reviewer advised against.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28, explicit choice in session |
| **Reasoning** | Small, test-backed follow-ups that close the certification layer |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Absolute per-profile floor + optional baseline non-regression | "didn't get worse" AND "still good" | relative-only gates |
| 2 | Token eligibility declared in rules; measured rows always eligible | model-facing universe only; never hide a measurement | all rows eligible |
| 3 | Persist failures filtered by `run_id`, global kept separately | runs cannot contaminate each other | root-global counter |
| 4 | Hardening eval calls `plan_roles`, contract validators and `build_delta` | oracle must not duplicate the logic it guards | recomputed arithmetic |
| 5 | Explicit delta/case paths confined by AllowedRoots | smaller trust surface for MCP/agent callers | documenting as authority inputs |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Floors/baselines for the other 9 evals | Review flagged only agentic-quality | Yes |
| Common eval-oracle framework | Large refactor beyond scope | Yes |
| New auditable-receipt type | Run-scoped failures solve the reported gap | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| E1: quality floor + token eligibility + ledger scoping | ✅ | Approved | No |
| E2: hardening eval on production paths + explicit path confinement | ✅ | Approved | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
The economy certification layer can still certify wrong outcomes: the
agentic-quality gate passes when every profile is equally wrong, token
coverage penalizes deterministic rows, persist failures leak across runs, the
hardening eval re-implements the logic it guards, and explicit delta/case
paths bypass the trust boundary.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Release guardian | A green eval must mean "good", not just "equally bad" |
| Maintainer reading stats | Pessimistic coverage and cross-run failures mislead |
| Agent hosts via MCP | Explicit paths are a residual arbitrary-read surface |

### Success Criteria (Draft)
- [ ] All-wrong corpus ⇒ `agentic-quality` `passed == false`
- [ ] Baseline regression ⇒ fails; equal/better ⇒ passes
- [ ] deterministic None + provider 1000 + role 500 ⇒ `complete`, 1500
- [ ] Run-A persist failure invisible to `stats --run-id B`
- [ ] Hardening eval would fail if `plan_roles` pools or delta classification regress
- [ ] `--changed ../secret.py` never read; out-of-root `--case-dir` refused
- [ ] All existing evals and the full suite pass

### Constraints Identified
- Offline, deterministic, no provider SDK; AF code + field + unlock, cataloged; bilingual docs in pairs.

### Out of Scope (Confirmed)
- New economy features; refactoring other evals.

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

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_EVAL_INTEGRITY.md`
