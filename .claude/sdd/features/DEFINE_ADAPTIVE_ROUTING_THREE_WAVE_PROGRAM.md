# DEFINE: Adaptive Routing Three-Wave Program

> Evolve capability routing into a bounded execution plan, evidence-backed evaluation loop and reusable expertise layer while preserving offline-first compatibility.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM` |
| **Date** | 2026-09-24 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 15/15 |

---

## Problem Statement

API Forge already ranks eligible capabilities and records scorecards, but the
runtime does not express the difference between a primary candidate, a
conditional fallback, parallel review, criticism and arbitration. The project
also needs stronger evidence/freshness semantics and a reusable expertise layer
so routing can evolve without losing deterministic safety or compatibility.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Runtime maintainers | Maintain routing, supervisor and policy code | Execution order is richer than the current `fallback_order` contract |
| Agent/skill authors | Publish capabilities and reusable knowledge | Agent identity, methodology and domain knowledge need cleaner boundaries |
| Operators/reviewers | Inspect runs, evidence and promotion decisions | Ranking, freshness, adversarial coverage and promotion state need explicit explanations |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Add an additive `RoutingPlan/v1` that distinguishes primary, conditional fallback, parallel candidates, reviewer, critic and referee. |
| **MUST** | Make supervisor execution consume the plan deterministically, preserving budgets, replay and existing `RoutingDecision` artifacts. |
| **MUST** | Add evidence-backed multidimensional scorecard signals with explicit freshness and adversarial evaluation support. |
| **MUST** | Add reusable expertise-pack bindings and allow multiple implementations to participate in one capability family. |
| **SHOULD** | Preserve static-routing fallback and expose plan, scorecard and pack limitations in receipts and unresolved fields. |
| **COULD** | Add a bounded complexity signal for future routing policy without making it a prerequisite for the three waves. |

**Priority Guide:**
- **MUST** = MVP fails without this (non-negotiable)
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes:

- [ ] Wave 1, Wave 2 and Wave 3 each land with a focused commit and an auditable build report.
- [ ] Existing routing and supervisor tests remain green, and legacy `RoutingDecision` JSON remains loadable after the new plan is introduced.
- [ ] A routed run persists a deterministic plan with explicit primary/fallback/parallel/reviewer/critic/referee roles and never treats every fallback as an unconditional primary invocation.
- [ ] Scorecard signals can represent observed, fresh, stale, unknown and unresolved states, and promotion refuses evidence that fails the configured eval gate.
- [ ] At least two implementations can be registered under one capability family without changing the public task request shape.
- [ ] Expertise-pack requirements are checked locally and missing or stale knowledge produces a named unresolved/gate result rather than an inferred success.
- [ ] No new wave requires network access, provider credentials, administrative installation or core-side external mutation.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Build an execution plan | A valid `RoutingDecision` has ranked candidates | The planner runs with the local policy | It emits `RoutingPlan/v1` with one primary and explicit role collections, stable digest and bounded counts |
| AT-002 | Conditional fallback | The primary invocation fails | The supervisor evaluates the plan | Only the next eligible fallback is started; parallel/reviewer roles are not silently treated as fallbacks |
| AT-003 | Legacy replay | A pre-plan `routing.json` contains `RoutingDecision/v1` | The run store loads the artifact | The decision remains readable and the runtime can derive a compatible plan |
| AT-004 | Plan gate | A plan is missing required evidence or exceeds a configured bound | The supervisor attempts execution | The run is `REVIEW` or `BLOCKED` with `AF-*`, field and unlock; no invocation is authorized |
| AT-005 | Freshness-aware signal | A scorecard signal has an expired observation window | Routing evaluates candidates | The signal is stale/unresolved and cannot silently promote a candidate as fresh |
| AT-006 | Adversarial eval gate | A candidate lacks required adversarial evidence or has a failed adversarial result | Feedback updates a scorecard | Quality is not promoted and the feedback records the blocking gap |
| AT-007 | Scorecard poisoning resistance | A result has no evidence, mismatched observation refs or an invalid metric | Feedback is submitted | The scorecard is rejected or remains unpromoted with a typed refusal |
| AT-008 | Multiple implementations | Two profiles share one capability family and have different pack/signal state | Routing is requested for the family | Both are assessed independently and ranking remains deterministic |
| AT-009 | Expertise-pack resolution | A profile requires a local pack that is absent or stale | Eligibility runs | The candidate is rejected with a structured `AF-*` unlock and no inferred pack support |
| AT-010 | Backward compatibility | Existing CLI/MCP contracts and fixtures are used | The three-wave suite runs | Existing surfaces remain valid, new fields are additive and all evidence remains replayable |

---

## Out of Scope

Explicitly NOT included in this feature:

- autonomous high-level `ask`, `improve`, `migrate` and `fix` orchestration;
- complete relation inference across all repository types;
- a separate `apiforge here` command;
- auto-update or remote synchronization of knowledge packs;
- symlink installation or automatic overwrite of host-owned files;
- task-level precedence before manifests stabilize;
- distributed workspace debate or a promise of total functional parity between hosts;
- live provider mutation, model SDK calls or network-dependent routing;
- making task complexity inference a hard prerequisite for the three waves.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Offline-first and hostless operation must remain valid | Use local YAML/JSON/contract data, replayable traces and no new network ingress |
| Technical | Existing contracts, CLI, MCP and receipts remain compatible | Add versioned fields/models and derive new plans from old decisions |
| Technical | Deterministic budgets and evidence gates remain authoritative | Bound role counts, fallback depth, retries, parallelism and promotion |
| Security | External mutation remains outside the core | Do not add provider writes; preserve host and CI mutation boundaries |
| Delivery | Each wave must be committed before the next wave begins | Keep migration and rollback visible in separate commits |

---

## Technical Context

| Aspect | Value | Notes |
|-------|-------|-------|
| **Deployment Location** | `src/apiforge/contracts`, `runtime`, `capabilities`, `evals`, `knowledge`, `rules` | Existing deterministic runtime and contract boundaries |
| **KB Domains** | `genai`, `prompt-engineering`, `testing`, `pydantic`, shared `component-model` | State-machine orchestration, structured validation, eval design and layer separation |
| **IaC Impact** | None | No infrastructure or provider mutation is required |

**Why This Matters:**

- **Location** → Keeps plan, signal, scorecard and pack behavior in existing governed layers.
- **KB Domains** → Design uses repository-aligned patterns rather than inventing a second agent model.
- **IaC Impact** → Confirms the feature remains local and replayable.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Existing `RoutingDecision/v1` can remain the persisted selection trace | A migration adapter and new receipt version would be needed | [x] |
| A-002 | The supervisor and `ControlPlane` can represent conditional dependencies | A dedicated plan executor would be required before Wave 1 | [x] |
| A-003 | Local knowledge packs can be addressed by stable domain/version identity | Expertise-pack resolution would need a new storage boundary | [x] |
| A-004 | Existing eval fixtures can be extended with adversarial and stale-signal cases | A separate corpus-ingestion phase would be needed | [x] |
| A-005 | The current branch is the intended delivery branch and PR #9 can receive the three-wave commits | A new branch/PR would be required | [x] |

**Note:** These assumptions are grounded by the codebase inspection and are
rechecked by the build and verification gates.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Routing semantics, evidence quality and expertise separation are explicit |
| Users | 3 | Maintainers, authors and operators are identified |
| Goals | 3 | Three waves and their boundaries are named |
| Success | 3 | Acceptance criteria cover behavior, compatibility, evidence and delivery |
| Scope | 3 | YAGNI removals and post-ship deferrals are explicit |
| **Total** | **15/15** | |

**Minimum to proceed: 12/15**

---

## Open Questions

None - ready for Design. Implementation decisions that do not change the
scope are recorded as autonomous decisions in the build report.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-24 | define-agent | Captured the confirmed three-wave program |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DESIGN_ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM.md`
