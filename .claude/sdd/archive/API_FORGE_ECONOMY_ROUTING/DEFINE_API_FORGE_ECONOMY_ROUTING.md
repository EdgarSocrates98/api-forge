# DEFINE: API Forge Economy — Economic Routing (Onda 3)

> Economy Plane for the runtime: profiles, budget envelopes, risk-invariant role floors, stop conditions, an escalation ladder, and risk-adaptive SDD profile selection.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_ROUTING |
| **Date** | 2026-09-27 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_ROUTING.md` |

---

## Problem Statement

The API Forge router and supervisor size execution by risk alone. Nothing bounds cost by operator preference, reserves calls for verification, stops once proof is reached, or matches SDD process weight to change risk. The result is that a trivial task can consume the same roles, calls and debate as a critical one, and cheaper paths cannot be chosen safely.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Operator | Runs `apiforge runtime run/resume/debate` locally or in CI | Cannot request a cheaper execution without risking an unsafe plan |
| Agent host (Claude/Codex/Devin) | Drives the runtime via MCP | Gets no explicit budget, stop signal or escalation reason |
| SDD author | Writes `docs/sdd/<feature>` chains | Must pick a profile by hand; a doc rename and a breaking migration can carry the same process |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | G1: `BudgetEnvelope/v1` and `EconomyPlan/v1` versioned contracts, registered and documented |
| **MUST** | G2: Profiles `economy`, `balanced` and `deep`, with limits defined in policy YAML. Resolution order is `--profile` > project manifest `economy_profile` > policy default `balanced` |
| **MUST** | G3: Risk escalation. The effective profile is ≥ the floor derived from `RiskComplexityAssessment` and `GraphImpactAssessment` (critical/irreversible → deep, complex/sensitive → balanced). The reason is recorded. Risk never downgrades the profile |
| **MUST** | G4: `RoutingDecision.economy` is an optional field. `build_routing_plan` trims optional roles (parallel, challengers, fallbacks beyond the envelope, roles not in `required_roles`) and never removes a `required_roles` entry. Trimmed roles are listed |
| **MUST** | G5: The supervisor enforces the envelope. `max_calls` becomes min(TaskSpec, envelope), debate `max_rounds` comes from the envelope, and the verification/synthesis reserve is held out of the investigation pool |
| **MUST** | G6: Stop conditions. When a deterministic result proves the answer (no unresolved critical, verification passed), execution stops and the remaining budget is not spent |
| **MUST** | G7: Exhaustion returns `status: unresolved` with `AF-BUDGET-EXHAUSTED`, `field` and `unlock`, and never downgrades silently |
| **MUST** | G8: Escalation ladder L0–L5 with deterministic triggers (unresolved, low confidence/gaps, material disagreement, critical unresolved). It reuses the existing debate and approval gate. The profile caps the ceiling and risk raises the floor |
| **MUST** | G9: Corpus `evals/corpus/economy-routing/` (15 cases, 5 risks × 3 profiles) and `apiforge evals economy-routing`, run through the fake adapter, with a baseline recorded from the current behaviour |
| **MUST** | G10: `--profile` on `runtime run/resume/debate` and the matching MCP tools. The `economy` block is visible in the persisted routing artifact |
| **SHOULD** | G11: Risk-adaptive SDD. `apiforge sdd classify` returns micro/low/medium/high from deterministic signals (contract diff, touched paths, policy keywords) mapped to `micro`/`quick`/`standard`/`critical` (or `migration` when cross-repo) |
| **SHOULD** | G12: New SDD profile `micro: [intent, verify, ship]`. `sdd check` refuses `AF-SDD-PROFILE-BELOW-RISK` when a feature carries a classification and declares a lower profile |
| **COULD** | G13: `AF-ECONOMY-ESCALATED` diagnostic surfaced in `runtime status` output |

---

## Success Criteria

- [ ] SC1: 15/15 corpus cases keep every `required_roles` entry under every requested profile (0 violations).
- [ ] SC2: In 100% of micro/low cases, the `economy` profile uses fewer or equal calls and strictly less fanout (parallel + challengers + fallbacks) than the recorded baseline plan, in at least one of the two measures.
- [ ] SC3: 100% of high/critical cases resolve to effective profile `deep`, whatever the requested profile.
- [ ] SC4: In 100% of cases where a deterministic resolver proves the answer, the run stops at ladder level L0/L1 and uses 0 specialist calls.
- [ ] SC5: 100% of budget-exhaustion cases end `unresolved` with `AF-BUDGET-EXHAUSTED`, and 0 silent downgrades.
- [ ] SC6: The verification reserve is never consumed by investigation (reserve ≥ configured share at the verification step in 100% of cases).
- [ ] SC7: `sdd classify` returns the expected class in 100% of its test cases (≥ 8 cases across the 4 classes). `sdd check` refuses below-risk profiles in its tests.
- [ ] SC8: Existing routing and runtime tests pass unchanged. The full suite and `sdd check` run once, at the end.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Default profile | TaskSpec without `--profile`, no manifest profile | `runtime run` | `economy.requested=balanced`, `effective=balanced`, source `default` |
| AT-002 | Precedence | Manifest `economy_profile: deep` | `runtime run --profile economy` | requested `economy`, source `flag` |
| AT-003 | Risk escalation | Irreversible/critical task | `runtime run --profile economy` | effective `deep`, `escalation_reason` names the risk band, `AF-ECONOMY-ESCALATED` diagnostic |
| AT-004 | Role invariant | Complex task (`reviewer`, `critic` required) | `--profile economy` | Plan keeps reviewer and critic. Only optional roles appear in `trimmed_roles` |
| AT-005 | Trim in low risk | Simple read-only task | economy vs baseline | 0 parallel/challengers/fallbacks; calls ≤ baseline |
| AT-006 | Supervisor cap | Envelope `provider_calls=2`, TaskSpec `max_calls=20` | run | At most 2 investigation calls plus the reserved verification call |
| AT-007 | Exhaustion | Fake adapter keeps returning unresolved | run with economy | `status: unresolved`, `AF-BUDGET-EXHAUSTED` with field/unlock, no downgrade |
| AT-008 | Stop condition | Deterministic step fully resolves | run with deep | Stops at L0/L1. No specialist/reviewer/debate calls |
| AT-009 | Ladder climb | Specialist returns low confidence, then reviewer disagrees | balanced | Climbs to L3, then L4 debate with `max_rounds` from the envelope |
| AT-010 | Ladder ceiling | Same as AT-009 | economy, non-critical | Stops at the profile ceiling with `unresolved`. No debate |
| AT-011 | Invalid profile | `--profile cheap` | run | Refused `AF-ECONOMY-PROFILE-INVALID` with field/unlock |
| AT-012 | Corpus gate | Corpus + recorded baseline | `apiforge evals economy-routing` | Report with per-case roles, calls, fanout, level. Exit ≠ 0 if SC1–SC6 fail |
| AT-013 | SDD classify | Change touching auth paths / breaking diff | `sdd classify` | `high` → `critical` profile, with the signals listed |
| AT-014 | SDD below risk | Feature classified `high`, declares `quick` | `sdd check` | Refused `AF-SDD-PROFILE-BELOW-RISK` |
| AT-015 | Legacy compatibility | Persisted `RoutingDecision`/`RoutingPlan` payload without `economy` | validate/load | Still validates. Runtime without a profile keeps the current role selection except for the default balanced limits |

---

## Out of Scope

- Wave 2: shared CAS cache, incremental graph, delta-first, dependency-aware invalidation.
- Wave 4: lazy expertise, capsule/delta debate, shadow budgets, agent anti-theater gate, capability-first pre-router filtering, supervisor consuming ContextCapsule, `graph_expansions`/`context_bytes` limits bound to capsules.
- Wave 5: compact MCP surface, log/test output slicing.
- Wave 6: economy × balanced × deep eval matrix with holdout/mutation, and economic champion/challenger.
- Quality-floor ranking (minimize cost subject to observed quality ≥ floor).
- Provider tiering, local models, monetary cost inside the envelope.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | No provider SDK, no network, deterministic | Ladder triggers use payload fields (confidence, gaps, disagreement), not model calls |
| Technical | `RoutingDecision/v1`/`RoutingPlan/v1` stay v1. New fields are optional and defaulted, and old payloads validate | Additive change only |
| Technical | Every refusal carries `AF-*`, `field` and `unlock`, cataloged in `docs/catalog-contract.md`. New contracts get `docs/contracts/*-v1.md` (release gate) | Docs updated with code |
| Technical | Supervisor changes are limited to reading limits, reserve, stop conditions and ladder triggers | Contain regression risk in the 35K module |
| Process | Targeted tests per task. Full suite once at the end with an out-of-repo `--basetemp` | Build plan |
| Process | Edits via apply_patch-equivalent. Tests and SDD artifacts updated together | Build plan |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/contracts/economy.py` (+ `BudgetEnvelope`, `EconomyPlan`), `src/apiforge/contracts/routing.py` (`RoutingDecision.economy`), `src/apiforge/contracts/workspace.py` (`ProjectManifest.economy_profile` optional), `src/apiforge/runtime/economy.py` (new: resolve/escalate/trim/ladder), `src/apiforge/runtime/routing.py`, `src/apiforge/runtime/supervisor.py`, `src/apiforge/debate/service.py`, `src/apiforge/rules/agentic_runtime.yaml` (profile limits), `src/apiforge/sdd/` (classify, `micro` profile, check), `src/apiforge/evals/economy_routing.py`, CLI + MCP, `evals/corpus/economy-routing/` | Extends existing modules |
| **KB Domains** | pydantic, testing, genai, anti-patterns, python | Contracts, deterministic tests, multi-agent budget patterns |
| **IaC Impact** | None | Local-first |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | The fake adapter can script confidence/gaps/disagreement per step to drive ladder triggers | Need a scripted-response extension to the fake adapter | [ ] |
| A-002 | The supervisor has a single place where `max_calls` and debate rounds are read | Enforcement spreads across several call sites. Higher regression risk | [ ] |
| A-003 | The "deterministic resolver proves the answer" signal already exists as a step result (e.g., contract-intel/impact verdict) | Define an explicit `deterministic_proof` field in the step payload | [ ] |
| A-004 | Adding optional `economy` to `RoutingDecision` does not break persisted fixtures (extra=forbid applies to readers of new payloads only) | Fixtures regenerated; document the compatibility note | [ ] |
| A-005 | `sdd classify` signals (contract diff classification, path globs, keywords) are enough to separate the 4 classes on the test set | Classification gaps become `unresolved` and never go below `standard` | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Concrete gap grounded in current router/supervisor/SDD code |
| Users | 3 | Three personas with specific pains |
| Goals | 3 | MoSCoW, 13 traceable goals |
| Success | 3 | Numeric, per-case gates on a deterministic corpus |
| Scope | 2 | Clear exclusions. Supervisor touch surface to be confirmed in Design (A-002) |
| **Total** | **14/15** | |

---

## Open Questions

- Q1 (Design): exact default limits per profile (calls, fanout, rounds, reserve share). Start from the brainstorm table and tune on the corpus.
- Q2 (Design): where `sdd classify` persists its classification (feature frontmatter `risk_class:` vs `evidence/`).

Neither blocks Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-27 | define-agent | Initial version from BRAINSTORM |
| 1.1 | 2026-09-27 | ship-agent | Shipped and archived |

---

## Next Step

**Ready for:** `/agentspec:workflow:build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_ROUTING.md`
