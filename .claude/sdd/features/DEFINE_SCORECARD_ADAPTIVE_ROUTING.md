# DEFINE: Scorecard-Adaptive Routing

> A deterministic, evidence-gated champion/challenger policy that uses fresh scorecards to adapt routing without starving new candidates.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | SCORECARD_ADAPTIVE_ROUTING |
| **Date** | 2026-09-25 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 15/15 |

---

## Problem Statement

API Forge already computes evidence-gated scorecards and uses their quality, cost and duration signals during routing, but it has no explicit adaptive policy for distinguishing verified champions from unproven challengers. Without that policy, fresh history is difficult to audit and new eligible implementations can be permanently disadvantaged by candidates with established history.

The feature must make historical scorecard evidence influence routing as a versioned, replayable assessment while preserving freshness limits, unresolved diagnostics, static fallback behavior and the no-external-mutation boundary.

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Runtime supervisor | Selects and executes bounded routing plans | Needs trusted history to influence selection without allowing stale or unverified scorecards to dominate |
| Capability owner | Maintains specialist and implementation profiles | Needs a bounded challenger opportunity for new implementations to earn evidence |
| Governance/evaluation owner | Reviews scorecards, gates and route explanations | Needs lane, freshness, evidence and gap provenance in the canonical decision |

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Produce a versioned `ScorecardRoutingAssessment/v1` from explicit local scorecard snapshots and policy inputs |
| **MUST** | Classify eligible candidates into champion, challenger or unresolved lanes using promoted history and freshness evidence |
| **MUST** | Prefer fresh promoted champions according to the existing risk/complexity objective order while reserving a policy-bounded challenger opportunity |
| **MUST** | Preserve scorecard refs, evaluation refs, freshness state, unresolved gaps and policy identity in `RoutingDecision/v1` and downstream plan data |
| **MUST** | Keep feedback and promotion evidence gates intact; no live provider calls, automatic external promotion or mutation may be introduced |
| **MUST** | Prove replay, freshness, anti-starvation, evidence preservation and mutation behavior with existing plus new local eval cases |
| **SHOULD** | Keep all new fields additive so callers that do not supply scorecard policy remain compatible |
| **COULD** | Add a dedicated explainability CLI/TUI view for lane decisions after the canonical payload is shipped |

**Priority Guide:**
- **MUST** = MVP fails without this
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

## Success Criteria

Measurable outcomes:

- [ ] **100%** of mandatory adaptive-routing golden, holdout, mutation and adversarial cases pass.
- [ ] **100%** of replay runs with identical request, scorecard snapshot and policy version produce identical adaptive assessment, routing decision, routing plan and stable digests.
- [ ] **100%** of stale, unresolved or unpromoted scorecards are excluded from champion eligibility.
- [ ] **100%** of eligible no-history candidates remain represented in the decision trace, with challenger selection bounded by the configured policy.
- [ ] **0** scorecard evidence refs, freshness diagnostics or unresolved gaps are silently dropped between assessment, routing, persistence and projection.
- [ ] **0** provider, network, database or external mutation calls are added to the adaptive routing path.

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Deterministic adaptive replay | The same request, scorecards, policy and capability registry are provided twice | Adaptive routing runs twice | Assessment, lane membership, candidate order, decision ID and plan ID are identical |
| AT-002 | Fresh champion preference | Two eligible candidates exist and one has fresh promoted quality history | The policy ranks candidates | The champion is preferred according to the inherited risk/complexity objective order and the reason is recorded |
| AT-003 | Bounded challenger opportunity | An eligible candidate has no promoted scorecard and the policy allows challenger exploration | The route is derived | The candidate is represented as a challenger and selected only within the configured bounded challenger slot |
| AT-004 | Freshness safety | A candidate has stale or unresolved scorecard observations | The adaptive assessment runs | The candidate cannot be champion-eligible; freshness and gap evidence remain visible |
| AT-005 | Evidence preservation | Scorecards include evaluation refs, observation refs and unresolved gaps | The decision and plan are persisted/projected | All refs and gaps survive canonical serialization without recomputation |
| AT-006 | Legacy compatibility | Existing routing callers omit adaptive scorecards and use the shipped A policy | Routing and plan building run | Existing selection, fallback, role disjointness and risk/complexity behavior remain valid |
| AT-007 | Feedback gate integrity | Runtime results are missing evidence or the evaluation gate is not PASS | Scorecard feedback is requested | No promoted scorecard is persisted and the existing `AF-*` refusal/gap is preserved |
| AT-008 | Policy mutation replay | Challenger slot, freshness rule or promotion threshold is changed in a local policy fixture | The same input is classified | The adaptive assessment identity changes or the result becomes gated as specified; no silent fallback occurs |

## Out of Scope

Explicitly NOT included in this feature:

- Live provider-backed shadow execution or comparative telemetry.
- Automatic champion promotion, retirement, degraded lifecycle or external state mutation.
- Graph-derived cohorts or impact analysis; those belong to planned C.
- A generic weighted sum that replaces explicit risk/complexity objectives and gates.
- A new UI surface; existing read-only projections consume the canonical payload first.
- Changes to the shipped A risk/complexity semantics beyond additive adaptive routing metadata.

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Must use local typed contracts, YAML policy and existing scorecard persistence | The assessment is pure and replayable; no hidden defaults or provider state |
| Safety | Stale, unresolved and unpromoted history cannot authorize champion status | Adaptive routing must preserve explicit gaps and use the static route when evidence is insufficient |
| Compatibility | Existing `RoutingDecision/v1`, `RoutingPlan/v1`, routing roles and fallback bounds remain valid | New fields are additive and legacy callers remain valid |
| Evaluation | Existing golden/holdout/mutation/adversarial gates remain mandatory | New fixtures must cover champion, challenger, freshness and starvation behavior |
| Runtime | No external network/database/provider calls or mutation | Build and verification are local-only |
| Determinism | Input collections, lane assignment, ranking and IDs must be canonicalized | Reordered scorecard inputs cannot change the result |

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/contracts`, `src/apiforge/runtime`, `src/apiforge/capabilities`, `src/apiforge/rules`, `tests`, `docs/contracts` | Reuse current scorecard/routing seams and local policy files |
| **KB Domains** | `genai`, `pydantic`, `python`, `testing` | Evaluation-gated adaptation, typed validators, pure transformations and fixture-driven tests |
| **IaC Impact** | None | No infrastructure, provider, database or deployment change |

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|-----------------|------------|
| A-001 | `AgentScorecard` is the authoritative local snapshot for historical candidate evidence | A new evidence store would be required before adaptive routing | [x] Existing contract and persistence inspected |
| A-002 | `quality_promoted`, `evaluation_count` and freshness are sufficient for MVP champion eligibility | Additional promotion metadata would be needed | [x] Existing scorecard builder and feedback gate inspected |
| A-003 | `RoutingDecision/v1` is the canonical persistence boundary | Multiple surfaces could drift if a sidecar were introduced | [x] Existing store and projections inspected |
| A-004 | The challenger path can remain bounded and read-only in B | Live shadow scheduling would be required for the MVP | [x] User requested autonomous B within the offline-first project contract |
| A-005 | Existing capability family/implementation metadata identifies comparable candidates | New registry identity fields would be required | [x] Current capability registry inspected |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Existing scorecards influence ranking but have no explicit champion/challenger policy |
| Users | 3 | Runtime, capability owners and governance/evaluation owners are identified |
| Goals | 3 | Contract, policy, safety and compatibility goals are prioritized with explicit boundaries |
| Success | 3 | Replay, freshness, bounded exploration and evidence-preservation criteria are testable |
| Scope | 3 | B MVP and live/graph/UI exclusions are explicit |
| **Total** | **15/15** | High confidence; ready for Design |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

## Open Questions

None - ready for Design. Design will fix the initial local policy defaults and exact additive field shape without expanding the confirmed scope.

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-25 | define-agent | Captured autonomous B requirements from the validated brainstorm |

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_SCORECARD_ADAPTIVE_ROUTING.md`
