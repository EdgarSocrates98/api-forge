# BRAINSTORM: Scorecard-Adaptive Routing

> Exploratory session to turn the planned B extension into a deterministic, evidence-gated routing slice

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | SCORECARD_ADAPTIVE_ROUTING |
| **Date** | 2026-09-25 |
| **Author** | brainstorm-agent |
| **Status** | Ready for Define |

---

## Initial Idea

**Raw Input:** Start planned extension B after shipping risk-aware routing: let verified historical scorecards influence candidate routing while preserving deterministic replay, freshness boundaries, evidence provenance, challenger access and the static fallback. Continue without provider calls, live telemetry, external mutation or automatic promotion.

**Context Gathered:**
- `AgentScorecard` already records quality, multidimensional scores, cost, duration, freshness, evidence refs and evaluation case refs.
- `build_scorecard` and `update_scorecard` already prevent unverified feedback from becoming a promoted scorecard.
- `route_capabilities` already consumes scorecards for quality/cost/duration ordering, but its policy does not expose champion/challenger lanes or an anti-starvation rule.
- `EvolutionPolicy` and `PromotionGate` already provide bounded, evidence-gated local/replay/shadow states with a static fallback.
- The shipped A feature owns risk/complexity classification; B should enrich candidate selection from verified history without replacing A's canonical assessment.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/contracts`, `src/apiforge/runtime`, `src/apiforge/capabilities`, `src/apiforge/rules`, tests and contract docs | Add an additive adaptive assessment, policy data and lane-aware routing while preserving existing v1 fields |
| Relevant KB Domains | `genai`, `pydantic`, `python`, `testing` | Use evaluation-gated feedback, typed immutable contracts, pure transformations and fixture-driven replay tests |
| IaC Patterns | N/A; local control-plane policy only | No infrastructure or provider dependency is needed |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | What is the purpose of B? | Make verified historical performance influence routing without allowing a known champion to permanently starve new implementations | Requires explicit champion/challenger lanes and a bounded exploration rule, not only a richer scalar score |
| 2 | Who consumes the result? | Runtime supervisor, routing/experience projections, operators and governance/evaluation owners | One canonical adaptive assessment must be embedded in the routing decision and remain explainable to every read-only surface |
| 3 | Which constraints dominate? | Deterministic offline replay, freshness-aware evidence, bounded execution and no external mutation | Scorecard snapshots and policy versions must be explicit inputs; stale or unresolved history cannot authorize promotion |
| 4 | What defines success? | Identical scorecard snapshots reproduce the same lane assignment and order; fresh verified history can change order; unseen candidates receive a bounded challenge opportunity | Evals need replay, freshness, champion/challenger, starvation and mutation cases |
| 5 | Which samples ground the work? | Existing scorecard, feedback, routing, evolution and adaptive-routing fixtures/tests only | The implementation must extend local fixtures and preserve existing golden/holdout/mutation/adversarial gates |

**Minimum Questions:** 5 (to ensure clarity before proceeding)

---

## Sample Data Inventory

> Samples improve LLM accuracy through in-context learning and few-shot prompting.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `src/apiforge/rules/agent_profiles.yaml`; `src/apiforge/rules/agentic_runtime.yaml` | Present | Local capabilities, profiles, routing policy and evolution policy |
| Output examples | `src/apiforge/capabilities/scorecard.py`; `src/apiforge/runtime/feedback.py`; `src/apiforge/runtime/routing.py` | Present | Scorecard construction, evidence-gated persistence and current ranking behavior |
| Ground truth | `tests/runtime/test_feedback.py`; `tests/runtime/test_routing.py`; `tests/runtime/test_promotion.py` | Present | Verified expectations for scorecard promotion, freshness and evidence gates |
| Related code | `tests/evals/cases/adaptive_routing.yaml`; `tests/fixtures/agentic_runtime/evolution_cases.yaml`; `prompt_evo_proxima_oportunidade.md` | Present | Existing eval categories and the documented B roadmap: champion/challenger, shadow evaluation and starvation prevention |

**How samples will be used:**

- Define fresh, stale, unresolved, missing and promoted scorecard snapshots.
- Prove that changing only scorecard evidence changes lane/order deterministically.
- Prove that a new challenger remains eligible and receives a bounded route opportunity.
- Preserve existing evidence-gated feedback and four-way evaluation coverage.
- Use current refusal and unresolved formats for invalid or insufficient scorecard history.

---

## Approaches Explored

### Approach A: Snapshot-Backed Champion/Challenger Policy ⭐ Recommended

**Description:** Add a versioned adaptive assessment that classifies eligible candidates into champion, challenger or unresolved lanes from local scorecard snapshots. Rank champions by the existing risk/complexity objective order, reserve a policy-bounded challenger slot, and record all lane decisions, freshness and evidence in the canonical routing decision.

**Pros:**
- Preserves deterministic replay because scorecards and policy version are explicit inputs.
- Prevents new implementations from starving while keeping verified champions preferred.
- Reuses current scorecard, freshness, evidence gate and routing seams.
- Keeps external shadow execution and promotion outside the core.

**Cons:**
- Requires a clear definition of promoted history and a bounded exploration policy.
- A challenger slot is a governance mechanism, not proof that the challenger is better.

**Why Recommended:** The codebase already has typed scorecards, freshness states, local persistence, evidence-gated feedback and stable ranking. The `genai` evaluation-framework pattern supports evaluation-backed adaptation, while the `pydantic` and `testing` domains support typed validation and fixture gates. Codebase match plus KB pattern gives strong confidence (0.95).

---

### Approach B: Single Weighted Historical Score

**Description:** Combine quality, cost, duration and freshness-adjusted history into one weighted scalar and sort all candidates by that value.

**Pros:**
- Compact ranking implementation.
- Easy to tune when objective weights are stable.

**Cons:**
- Hides hard evidence and freshness boundaries behind a number.
- Makes safety and verification objectives difficult to audit.
- New candidates with no history can be starved indefinitely.
- A weight change can silently alter policy semantics across risk classes.

**Why not recommended:** The repository already favors lexicographic objectives and explicit gates. A generic weighted score would weaken explainability and make unresolved history look more confident than it is.

---

### Approach C: Live Shadow Runner and Automatic Promotion

**Description:** Execute champion and challenger concurrently against live/provider-backed tasks, compare outcomes, and automatically promote the winner.

**Pros:**
- Produces direct comparative evidence.
- Could accelerate champion replacement after enough observations.

**Cons:**
- Adds provider/runtime side effects and cost to routing.
- Requires scheduling, isolation, rollback and human policy gates.
- Makes offline replay depend on live state unless snapshots are carefully captured.

**Why not recommended:** This is a later extension after the local adaptive assessment is proven. The current `PromotionGate` explicitly keeps external mutation and production claims outside the core.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A: Snapshot-Backed Champion/Challenger Policy |
| **User Confirmation** | 2026-09-25 — user explicitly requested autonomous development of planned B after A shipped |
| **Reasoning** | It delivers scorecard-adaptive routing now with a bounded challenger path, while preserving A's deterministic/offline boundary and leaving live shadow promotion as a separately governed extension |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Use an additive `ScorecardRoutingAssessment/v1` nested in `RoutingDecision/v1` | Keeps one canonical persisted result and prevents surface-specific recomputation | Separate mutable scorecard route store |
| 2 | Treat a scorecard as champion-eligible only when quality is promoted, history exists and freshness is not stale/unresolved | Prevents unverified or expired history from dominating routing | Trust any scorecard file with a numeric quality score |
| 3 | Reserve a bounded challenger slot for eligible candidates without champion evidence | Prevents starvation while retaining champion preference | Always rank unknown candidates last |
| 4 | Preserve unresolved scorecard gaps and evidence refs in the assessment | Missing history is an evidence state, not a confident negative score | Coerce missing history to zero quality |
| 5 | Keep live shadow execution, auto-promotion and external telemetry out of B MVP | Maintains offline-first scope and existing promotion boundaries | Activating `adaptive_plan` as a side effect of routing |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Live provider-backed shadow execution | Requires external state, isolation, cost and new approval gates | Yes — separate shadow-routing design |
| Automatic champion promotion | Promotion requires comparative evidence, rollback and policy ownership beyond routing | Yes — separate lifecycle/promotion design |
| Generic weighted score across all objectives | Obscures risk/evidence semantics and invites starvation | No for the core policy; explicit lexicographic lanes remain preferred |
| Graph-derived scorecard cohorts | B should consume verified scorecards only; graph impact belongs to C | Yes — planned C integration |
| New UI surface | Existing projections can expose the canonical assessment first | Yes — explainability/TUI enhancement later |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept | ✅ | User authorized autonomous B execution after A shipment | No |
| Component breakdown | ✅ | Existing scorecard, routing and promotion seams support the bounded slice | No |
| Data flow | ✅ | Snapshot → lane assessment → ranking → canonical decision was accepted by the requested autonomous continuation | No |
| Error handling | ✅ | Stale/unresolved history remains visible and cannot become champion evidence | No |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

API Forge stores verified scorecards but does not yet expose a deterministic champion/challenger policy that uses fresh historical evidence for routing while preventing new candidates from being starved.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Runtime supervisor | Needs historical quality to influence selection without trusting stale or unverified scorecards |
| Capability owner | Needs a challenger path so new implementations can earn evidence rather than remain permanently unselected |
| Governance/evaluation owner | Needs explainable lane, freshness, evidence and gap data for every adaptive route |

### Success Criteria (Draft)

- [ ] Replaying the same request, scorecard snapshot and policy version reproduces the same adaptive assessment, decision, plan and digest.
- [ ] Fresh promoted history can change candidate ordering according to the existing risk/complexity objective order.
- [ ] An eligible candidate without promoted history receives at most the configured challenger opportunity and is never silently discarded.
- [ ] Stale, unresolved or unverified scorecards cannot make a candidate champion-eligible.
- [ ] Existing feedback, promotion, golden, holdout, mutation and adversarial gates remain green.

### Constraints Identified

- Offline-first and deterministic; no provider, network, live database, clock or external mutation dependency.
- Scorecard snapshots, policy identity, lane assignment and evidence refs must be part of replay identity.
- Risk/complexity assessment from A remains authoritative for objective order and required roles.
- Existing routing, plan, fallback, evidence and refusal contracts remain compatible through additive fields.
- No automatic champion promotion or live shadow execution in this MVP.

### Out of Scope (Confirmed)

- Live shadow execution and provider-backed comparative telemetry.
- Automatic lifecycle transitions such as champion, challenger, degraded or retired persisted as external state.
- Graph-aware cohorts and impact-derived scorecard selection.
- Generic weighted-sum ranking that replaces explicit objectives and gates.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 discovery questions, including sample collection |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 5 |
| Validations Completed | 4 checkpoints |
| Duration | Autonomous repository-grounded session |
| Unresolved gaps | Threshold calibration and future live shadow lifecycle remain deferred; MVP boundary is ready for Define |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_SCORECARD_ADAPTIVE_ROUTING.md`
