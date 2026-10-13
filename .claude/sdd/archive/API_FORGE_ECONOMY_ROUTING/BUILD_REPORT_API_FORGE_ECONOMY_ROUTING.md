# BUILD REPORT: API Forge Economy — Economic Routing (Onda 3)

> Implementation report for API_FORGE_ECONOMY_ROUTING

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_ROUTING |
| **Date** | 2026-09-27 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_ROUTING.md](../features/DEFINE_API_FORGE_ECONOMY_ROUTING.md) |
| **DESIGN** | [DESIGN_API_FORGE_ECONOMY_ROUTING.md](../features/DESIGN_API_FORGE_ECONOMY_ROUTING.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 25/25 manifest entries |
| **Files Created** | 38 new (incl. 15 corpus cases, 9 SDD docs + 2 evidence, 4 contract docs) + 21 modified |
| **Lines of Code** | ~620 new in `src/` (economy module, supervisor staging, risk classifier, eval) |
| **Build Time** | 1 session |
| **Tests Passing** | 1109/1110 full suite (1 skipped); 1 pre-existing failure (orphan file) |
| **Agents Used** | 0 delegated (direct, as in Wave 0/1) |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1–4 | Contracts `BudgetEnvelope`, `LadderStep`, `EconomyPlan`, `RiskClassification`; `RoutingDecision.economy`; `ProjectManifest.economy_profile`; registry/exports | (direct) | ✅ Complete | - | Additive, optional |
| 5–6 | `rules/economy_profiles.yaml`, `runtime/economy.py` | (direct) | ✅ Complete | - | resolve/floor/envelope/trim/proof/triggers |
| 7–8 | Supervisor staging (L0 stop, L2 floor, L3 escalation, L4 ceiling, L5 gate), effective policy, reserve, exhaustion, economy block | (direct) | ✅ Complete | - | Trim applied by supervisor via `apply_economy` |
| 9–10 | `--profile` on `runtime run/resume/debate` (CLI + MCP) | (direct) | ✅ Complete | - | |
| 11–13 | `sdd/risk.py`, `micro` profile, `AF-SDD-PROFILE-BELOW-RISK`, `sdd classify` | (direct) | ✅ Complete | - | |
| 14–15 | `evals/economy_routing.py`, 15-case corpus, `evals economy-routing` | (direct) | ✅ Complete | - | Gates pass |
| 16–17 | Catalog, `docs/sdd-contract.md`, 4 contract docs | (direct) | ✅ Complete | - | Release-gate parity |
| 18–22 | Tests | (direct) | ✅ Complete | - | 57 targeted |
| 23–25 | SDD chain, `api-forge-sdd` skill + mirrors, README | (direct) | ✅ Complete | - | `sdd check` ok |

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | all | DESIGN patterns; existing assessment/ControlPlane/run_bounded conventions |

---

## Files Created

| File | Verified | Notes |
| ---- | -------- | ----- |
| `src/apiforge/runtime/economy.py` | ✅ | Economy Plane core |
| `src/apiforge/rules/economy_profiles.yaml` | ✅ | Limits, floors, triggers |
| `src/apiforge/sdd/risk.py` | ✅ | Deterministic classifier |
| `src/apiforge/evals/economy_routing.py` | ✅ | Corpus runner |
| `evals/corpus/economy-routing/*.yaml` (15) + README | ✅ | Ground truth |
| `tests/runtime/{economy_support,test_economy_plan,test_economy_supervisor}.py`, `tests/contracts/test_economy_routing_contracts.py`, `tests/sdd/test_risk_classify.py`, `tests/evals/test_economy_routing_eval.py` | ✅ | |
| `docs/contracts/{BudgetEnvelope,EconomyPlan,LadderStep,RiskClassification}-v1.md` | ✅ | |
| `docs/sdd/API_FORGE_ECONOMY_ROUTING/*` | ✅ | profile `standard`, `risk_class: medium` (self-classified) |

Modified: `contracts/{economy,routing,workspace,registry,__init__}.py`, `runtime/{supervisor,runner}.py`, `sdd/{checks.py,profiles.yaml}`, `cli.py`, `cli_governance.py`, `mcp/tools.py`, `docs/{catalog-contract,sdd-contract}.md`, README, 4× `api-forge-sdd/SKILL.md`, `tests/application/test_runtime_experience.py`, `tests/sdd/test_load.py`.

---

## Verification Results

### Lint Check

```text
ruff check src tests -> All checks passed!
ruff format --check src tests -> 720 files already formatted
```

**Status:** ✅ Pass

### Type Check

```text
mypy src/apiforge (strict) -> Success: no issues found in 382 source files
```

**Status:** ✅ Pass

### Tests

```text
Full suite (once, --basetemp E:/afpt): 1109 passed, 1 skipped, 1 failed
  FAILED tests/scripts/test_check_release.py -> only "agent mirror drift: .claude/agents/README.md (orphan)" (pre-existing)
Targeted: 57 passed
apiforge evals economy-routing -> passed: true (4/4 gates, 15 cases)
apiforge sdd check --root docs/sdd -> ok: true, refused: [], unresolved: []
```

**Status:** ✅ Feature green | ❌ 1 pre-existing repository failure

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | Supervisor invokes all roles concurrently; no sequential ladder existed | Staged execution: L2 = primary + risk roles (unchanged), L3 only on triggers via a pre-planned control step | medium |
| 2 | `ControlPlane.start` consumes a call; more initial roles than calls raised `AF-CONTROL-BUDGET` | Economy prioritizes primary + reviewers/critic/referee, drops the rest and reports `AF-BUDGET-EXHAUSTED` | small |
| 3 | Resume re-trimming would strand steps of already-planned (incl. legacy) control runs | Resume applies the call cap only, never re-trims | small |
| 4 | `test_runtime_experience_resume_executes_only_pending_step` encoded pre-economy fanout | Test now runs the first execution with `economy_enabled=False` (legacy-run resume) | small |
| 5 | `test_profiles_cover_all_four` pinned exactly 4 SDD profiles | Updated for the intentional `micro` profile | none |
| 6 | Release gate only recognizes codes as standalone quoted literals | `ESCALATED` / `RISK_UNRESOLVED` constants; `AF-SDD-*` documented in `docs/sdd-contract.md` | small |
| 7 | Dogfooding `sdd classify` on this feature returned `low` although it changes a versioned contract | `contracts/` and `schemas/` paths now classify as `medium`; test added | small |
| 8 | Full suite with the long scratchpad `--basetemp` failed 3 build/worktree tests (exit 2) | Windows path-length limit in git worktrees; full suite run with short out-of-repo `--basetemp E:/afpt` → green | small |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|--------------------|-------|-----------|
| 1 | Where trims are applied | Inside `build_routing_plan` vs supervisor after plan | Supervisor via `apply_economy` | Keeps `build_routing_plan` pure; economy plan needs decision + catalog kinds |
| 2 | L3 escalation reviewer | Invent optional reviewer vs first unused eligible reviewer | First unused reviewer in `fallback_order` | Uses real catalog; no synthetic roles |
| 3 | Corpus baseline | Recorded file vs live `economy_enabled=False` | Live baseline | Same code path, cannot drift; documented deviation |
| 4 | Critical corpus shape | Force runtime vs report review-blocked | Plan metrics + `review-blocked` calls | Existing TaskSpec review blocks irreversible runs before routing; no estimation |
| 5 | L0 proof matching | Whole run JSON vs ran steps only | Ran steps + terminal `awaiting_supervision` | Inputs cannot count as proof |
| 6 | Debate forcing | Ceiling always vs risk-forced exception | Critic-risk or effective `deep` forces L4 | Risk invariant beats profile ceiling |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| Trim in supervisor (`apply_economy`) instead of inside `build_routing_plan` | See decision 1 | None functionally |
| Resume does not re-trim | Protects legacy/planned control runs | Resume honors original plan roles |
| Live baseline for corpus | See decision 3 | No `baseline.json` for this corpus |
| Shape `small` instead of `simple` | Size S resolves to `moderate` complexity with current risk policy | Ground truth unchanged |
| Extra codes `AF-ECONOMY-ROLE-INVARIANT`, `AF-ECONOMY-ESCALATION-NOT-USED` | Invariant refusal and control-step note | Cataloged |

---

## Blockers (if any)

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| Release gate fails on pre-existing untracked `.claude/agents/README.md` | Commit with mirrors or remove | Repository owner |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Default profile | ✅ | `test_default_profile_is_balanced`, `test_default_profile_is_balanced_from_policy` |
| AT-002 | Precedence | ✅ | `test_flag_wins_over_manifest`, `test_manifest_profile_is_read_from_project_yaml`, CLI `requested_source == flag` |
| AT-003 | Risk escalation | ✅ | `test_risk_escalates_but_never_downgrades`, `test_sensitive_request_for_economy_escalates` |
| AT-004 | Role invariant | ✅ | `test_trim_keeps_required_roles_and_lists_removed`, `test_trim_refuses_to_change_risk_roles`, corpus `role_invariant` |
| AT-005 | Trim in low risk | ✅ | `test_economy_keeps_required_reviewer_and_cuts_optional_capacity`, corpus `economy_cheaper_low_risk` |
| AT-006 | Supervisor cap | ✅ | `test_task_budget_caps_calls_and_reports_exhaustion` |
| AT-007 | Exhaustion | ✅ | same test: `AF-BUDGET-EXHAUSTED`, `status: unresolved`, `final_status: REVIEW` |
| AT-008 | Stop condition | ✅ | `test_deterministic_proof_stops_before_any_agent_call`, `test_deterministic_proof_levels` |
| AT-009 | Ladder climb | ✅ | `test_low_confidence_escalates_to_reserved_review` (L3), `test_balanced_allows_bounded_debate` (L4) |
| AT-010 | Ladder ceiling | ✅ | `test_economy_ceiling_blocks_debate_without_downgrade` |
| AT-011 | Invalid profile | ✅ | `test_invalid_profile_is_refused_with_field_and_unlock`, `test_cli_profile_flag_and_invalid_profile` |
| AT-012 | Corpus gate | ✅ | `tests/evals/test_economy_routing_eval.py`, `apiforge evals economy-routing` |
| AT-013 | SDD classify | ✅ | `test_classify_maps_signals_to_minimum_profile`, `test_classify_uses_contract_diff` |
| AT-014 | SDD below risk | ✅ | `test_sdd_check_refuses_profile_below_classified_risk` |
| AT-015 | Legacy compatibility | ✅ | `test_legacy_routing_decision_payload_still_validates`, `test_legacy_project_manifest_still_validates`, resume of legacy run |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| SC1 role invariant | 15/15 | 15/15 | ✅ |
| SC2 economy cheaper for low risk | 100% | small/moderate economy: fanout 5→0, calls 6→2 | ✅ |
| SC3 critical ⇒ deep | 100% | 3/3 critical cases deep | ✅ |
| SC4 L0 stop, 0 specialist calls | 100% | yes (test) | ✅ |
| SC5 exhaustion explicit | 100% | yes | ✅ |
| SC6 reserve intact at verification | 100% | `reserve_left_at_verification ≥ reserve_calls` (test) | ✅ |
| SC7 classify cases | ≥ 8 | 11 parametrized + 5 others | ✅ |
| SC8 existing tests + sdd check | green | green except pre-existing orphan | ⚠️ |

Observation (pre-existing, not introduced): for `sensitive` tasks the risk policy requires a reviewer but no reviewer is eligible in the current catalog, so the baseline plan already lacks it; economy does not change that.

---

## Final Status

### Overall: ✅ COMPLETE (with one pre-existing repository blocker)

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] All verification checks pass (lint, types, feature tests, eval, sdd check)
- [ ] All tests pass — 1 pre-existing release-gate failure (orphan `.claude/agents/README.md`)
- [x] No blocking issues introduced by this feature
- [x] Acceptance tests verified
- [x] Ready for /ship

---

## Next Step

**If Complete:** `/agentspec:workflow:ship .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_ROUTING.md`
