# DEFINE: API Forge Economy Hardening 2 — Eval Integrity

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EVAL_INTEGRITY |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 15/15 |
| **Source** | [BRAINSTORM](./BRAINSTORM_API_FORGE_ECONOMY_EVAL_INTEGRITY.md) · `prompt_evo_new_economy.md` |
| **Branch** | `codex/economy-eval-integrity` |

---

## Problem Statement

The economy certification layer can still certify wrong outcomes: the
agentic-quality gate passes when every profile is equally wrong, token
coverage counts deterministic rows as unmeasured model calls, ledger persist
failures leak across runs, the hardening eval re-implements the logic it
guards, and explicit `context delta`/case paths bypass the trust boundary.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Release guardian | Certifies economy changes | A green eval must mean "good", not "equally bad" |
| Maintainer | Reads `economy stats` | Pessimistic coverage; another run's failure marks this run |
| Agent hosts via MCP | Pass paths to verbs | Explicit paths are a residual arbitrary-read surface |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | `agentic-quality`: per-profile absolute floor (`--min-accuracy`, default 1.0) + optional `--baseline` non-regression |
| **MUST** | Token coverage denominator = token-eligible rows only (`rules/token_eligibility.yaml`, measured rows always eligible) |
| **MUST** | Persist failures scoped by `run_id` (`persist_failures_for_run` vs `persist_failures_global`) |
| **MUST** | `economy-hardening` budget/delta cases run `plan_roles`, contract validators and `build_delta` |
| **MUST** | `--changed`, `--case-dir`, `--case` confined by AllowedRoots |
| **SHOULD** | Catalog, threat model and economy guide (EN + PT-BR) updated; MCP parity for new parameters |

---

## Success Criteria

- [ ] All-wrong recorded corpus ⇒ `passed == false` with `<profile>_quality_floor` gates false
- [ ] Baseline with higher accuracy than candidate ⇒ `<profile>_not_below_baseline` false
- [ ] Rows {deterministic: None, provider: 1000, runtime role: 500} ⇒ coverage `complete`, `observed_tokens == 1500`
- [ ] Run-A persist failure ⇒ `stats(run_id=B)` has `persist_failures_for_run == 0` and no `AF-ECONOMY-LEDGER-PERSIST`
- [ ] Hardening eval budget case fails if `plan_roles` returns a plan above the envelope (asserted via contract validator on real output); delta case uses a real analyzed fixture and `build_delta`
- [ ] `context delta --changed ../secret.py` never reads the file and reports `AF-PATH-OUTSIDE-ROOT`; out-of-root `--case-dir`/`--case` refused with field/unlock
- [ ] Full suite and all 10 economy evals pass

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Equally wrong | ground truth breaking, all profiles answer compatible | `evals agentic-quality` | `passed=false`, floor gates false |
| AT-002 | Baseline regression | baseline accuracy 1.0, candidate 0.5 | `--baseline` | not-below-baseline false |
| AT-003 | Baseline invalid | non-JSON / wrong schema | `--baseline` | refusal `AF-EVALS-BASELINE-INVALID` |
| AT-004 | Token eligibility | deterministic None + provider 1000 + role 500 | `economy stats` | complete, 1500 |
| AT-005 | No eligible rows | only deterministic rows | `economy stats` | `unresolved` |
| AT-006 | Run isolation | failure on run A | `stats --run-id B` | 0 for run, global 1 |
| AT-007 | Hardening real paths | corpus | `evals economy-hardening` | budget/delta via production code |
| AT-008 | Changed traversal | `--changed ../secret.py` | `context delta` | unresolved note, not read |
| AT-009 | Case dir escape | `--case-dir` outside roots | delta / capsule / evidence | refused `AF-PATH-OUTSIDE-ROOT` |

---

## Out of Scope

- New economy features; floors for the other 9 evals; a common eval framework.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Security | No provider SDK; offline | Evals use FakeModelAdapter/recorded outputs |
| Compatibility | Additive contract/CLI changes | Defaults keep current behavior where safe |
| Governance | AF code + field + unlock, cataloged; bilingual docs | Release gate parity |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/{evals,economy,context,evidence,rules}`, `cli.py`, `mcp/tools.py` | |
| **KB Domains** | catalog contract, threat model, economy guide; agentspec python/testing | |
| **IaC Impact** | None | |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Model-facing ledger verbs are `runtime role:*` today; `provider`/`transcript` are reserved prefixes | Rule gains prefixes | [x] only role rows are emitted by the runtime |
| A-002 | Default `--case-dir` (`<root>/.apiforge/case`) is inside the root | none | [x] |
| A-003 | Existing agentic-quality corpus stays at 1.0 so floor 1.0 passes | Floor default revisited | [x] last run 1.0/profile |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Each gap verified in code |
| Users | 3 | Three personas |
| Goals | 3 | MoSCoW |
| Success | 3 | Numeric, test-mapped |
| Scope | 3 | Explicit out of scope |
| **Total** | **15/15** | |

---

## Open Questions

None.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial from BRAINSTORM |

---

## Next Step

**Ready for:** `/agentspec:workflow:design .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_EVAL_INTEGRITY.md`
