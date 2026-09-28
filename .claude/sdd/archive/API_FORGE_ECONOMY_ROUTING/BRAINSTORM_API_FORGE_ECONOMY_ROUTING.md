# BRAINSTORM: API Forge Economy — Economic Routing (Onda 3)

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_ROUTING |
| **Date** | 2026-09-27 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** `prompt_evo_economy.md` — "vamos seguir com os demais faltantes do prompt". Waves 0–1 shipped (`2cd00b5`, archive `API_FORGE_ECONOMY_CONTEXT_GATEWAY`). This cycle covers Wave 3 (Economic Routing / Economy Plane) plus Risk-adaptive SDD (§19) and the full escalation ladder (§11).

**Context Gathered:**
- `contracts/routing.py`: `RoutingPolicy`, `RoutingRequest`, `RoutingDecision` (already carries `risk_complexity`, `graph_impact`, `scorecard_routing`, `shadow_evaluation` assessments), `RoutingPlan` with bounded roles.
- `runtime/routing.py::build_routing_plan` derives `required_roles` from `RiskComplexityAssessment` + `GraphImpactAssessment`.
- `runtime/supervisor.py` already bounds calls (`policy.max_calls`, `run_bounded`, `AF-ROUTING-FALLBACK-BUDGET`) and has approval gates and debate opening.
- `debate/service.py` has `max_rounds` / `retry_budget`.
- `sdd/profiles.yaml`: `quick`, `standard`, `critical`, `migration`; no risk-driven selection.
- Fixtures: `tests/fixtures/agentic_runtime/{risk_complexity_cases,routing_cases,kernel_scenarios,fake_responses}.yaml`.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/contracts/economy.py` (+), `src/apiforge/runtime/{economy.py,routing.py,supervisor.py}`, `src/apiforge/debate/service.py`, `src/apiforge/sdd/`, `src/apiforge/evals/`, CLI/MCP | Plug into existing assessment pattern |
| Relevant KB Domains | pydantic, testing, genai (multi-agent orchestration), anti-patterns, python | Versioned contracts, deterministic tests, agent-budget patterns |
| IaC Patterns | N/A | Local-first, no provider SDK |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Which slice this cycle? | Wave 3 first | Waves 2, 4, 5, 6 stay target architecture |
| 2 | What proves it works? | Deterministic routing corpus: economy cuts fanout/roles/debate in micro/low, never removes risk-required roles in high/critical | Gate on role invariant + reduction, no LLM |
| 3 | Where is the envelope enforced? | Plan + supervisor | Supervisor honors calls, debate rounds, verification reserve, stop conditions |
| 4 | Where does the profile come from? | `--profile` > project manifest/policy > default `balanced`; risk may escalate, never downgrade | Resolution chain + escalation reason recorded |
| 5 | Samples? | Extend existing fixtures | `evals/corpus/economy-routing/` ~15 cases run through fake adapter |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/agentic_runtime/risk_complexity_cases.yaml` | 5 | simple → critical/blocked with `expected_roles` |
| Input files | `tests/fixtures/agentic_runtime/routing_cases.yaml` | 3 | signal/safety routing |
| Output examples | `kernel_scenarios.yaml`, `fake_responses.yaml` | — | Fake adapter executes supervisor without LLM |
| Ground truth | `evals/corpus/economy-routing/*.yaml` (to create) | 15 | 5 risks × 3 profiles: expected effective profile, minimum roles, limits, ladder ceiling |
| Related code | `runtime/routing.py`, `runtime/supervisor.py`, `debate/service.py`, `sdd/profiles.yaml` | — | Integration points |

**How samples will be used:**
- Baseline = current `RoutingPlan` + supervisor run per case (no economy plane).
- Gate metrics: calls used, fanout, debate rounds, ladder level reached, role invariant.

---

## Approaches Explored

### Approach A: EconomyPlan as another routing assessment ⭐ Recommended

**Description:** New `BudgetEnvelope/v1` and `EconomyPlan/v1`; `RoutingDecision.economy` optional field (same pattern as `risk_complexity`, `graph_impact`, `scorecard_routing`); `build_routing_plan` applies trims but never removes `required_roles`; supervisor reads envelope limits and stop conditions.

**Pros:**
- Mirrors three existing assessments; `RoutingPlan` stays lean (prompt §68).
- Explainable (`trimmed_roles`, `escalation_reason`), testable without LLM.

**Cons:**
- Touches `RoutingDecision` and the 35K supervisor.

**Why Recommended:** direct codebase precedent (`RiskComplexityAssessment` → `required_roles` → `build_routing_plan`). Confidence 0.90.

---

### Approach B: Extend RoutingPolicy/RoutingPlan in place

**Description:** Budget/profile fields directly on policy and plan.

**Pros:**
- Fewer contracts.

**Cons:**
- Bloats `RoutingPlan`, mixes cost preference with role decision, weak "why trimmed" explanation.

---

### Approach C: Pre-router economic filter (capability-first)

**Description:** Profile filters candidates before eligibility/ranking.

**Pros:**
- Cuts fanout at the source.

**Cons:**
- Essentially Wave 4; risk invariant harder to guarantee.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-27 |
| **Reasoning** | Follows the established assessment pattern; keeps risk invariant explicit and auditable |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Profile = preference; risk/evidence = invariant | Economy must never mean accepting a worse answer (§17–18) | Profile as quality tier |
| 2 | Resolution: flag > manifest/policy > default `balanced`; escalate-only | Predictable, auditable | Risk-derived only; flag-only |
| 3 | Enforcement in supervisor, not only in plan | Budgets must bind execution | Plan-only; host-instruction-only |
| 4 | Exhaustion → `unresolved` + `AF-BUDGET-EXHAUSTED`, no silent downgrade | §65 | Degrade silently |
| 5 | Verification/synthesis reserved from the call budget | Never spend 100% investigating (§14) | Single pool |
| 6 | Stop conditions stop execution even with budget left | §33 | Spend remaining budget |
| 7 | Escalation ladder L0–L5 with deterministic triggers, reusing existing debate/approval mechanisms | §11, no new orchestrator | New orchestrator |
| 8 | Risk-adaptive SDD via deterministic classifier → existing profiles + new `micro`; `sdd check` refuses profile below risk | §19 | Manual profile choice only |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Quality floor in ranking (minimize cost s.t. quality ≥ floor) | Needs observed per-candidate quality scorecards | Yes — Wave 4/6 |
| Envelope `graph_expansions`/`context_bytes` bound to ContextCapsule in runtime | Requires supervisor to consume capsules | Yes — Wave 4 |
| Wave 2 cache/incremental (shared CAS, incremental graph, delta-first, invalidation) | Separate cycle | Yes |
| Wave 4 selective agentics (lazy expertise, capsule/delta debate, shadow budget, anti-theater gate) | Separate cycle | Yes |
| Wave 5 tool/host economy (compact MCP, log/test slicing) | Separate cycle | Yes |
| Wave 6 economy evals matrix, holdout, economic champion/challenger | Separate cycle | Yes |
| Provider tiering / local model | No provider dependency in core | Yes |
| Monetary cost in envelope | Cost only with explicit basis; already in `economy report` | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Economy Plane flow, profiles table, escalation ladder | ✅ | "ok" | No |
| Risk-adaptive SDD, corpus, gates, failures, surfaces | ✅ | "ok" | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
The API Forge router and supervisor size execution by risk only; nothing bounds cost by preference, reserves verification, stops when proof is reached, or matches SDD process weight to change risk — so trivial tasks can consume the same roles, calls and debate as critical ones.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Operator running `runtime run`/`route` | Cannot choose a cheaper path without risking unsafe plans |
| Agent hosts via MCP | No explicit budget or stop signal |
| SDD author | Same process for a doc rename and a breaking migration |

### Success Criteria (Draft)
- [ ] 15/15 corpus cases keep every `required_roles` entry under every profile.
- [ ] Economy profile uses fewer calls and fanout than current plan in all micro/low cases.
- [ ] High/critical cases resolve to effective profile ≥ deep regardless of requested profile.
- [ ] Stop condition ends execution at L0 when a deterministic resolver proves the answer.
- [ ] Budget exhaustion yields `unresolved` + `AF-BUDGET-EXHAUSTED`, never a silent downgrade.
- [ ] `sdd classify` maps the 4 risk classes to profiles; `sdd check` refuses a profile below classified risk.
- [ ] New AF codes cataloged; full suite + `sdd check` run once at the end.

### Constraints Identified
- No provider SDK, no network, deterministic.
- Existing runtime/routing tests and `RoutingPlan/v1` payloads must keep validating.
- Supervisor changes limited to reading envelope limits, reserve, stop and ladder triggers.
- Targeted tests per task; full suite once at the end (user preference).

### Out of Scope (Confirmed)
- Waves 2, 4, 5, 6 items listed in Features Removed.
- Quality-floor ranking and capsule-bound expansion budgets.
