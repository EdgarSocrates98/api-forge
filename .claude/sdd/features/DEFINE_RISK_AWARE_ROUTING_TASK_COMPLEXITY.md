# DEFINE: Risk-Aware Routing and Task Complexity

> A deterministic, evidence-preserving policy boundary that makes task risk and complexity shape routing objectives, verification depth and execution composition.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | RISK_AWARE_ROUTING_TASK_COMPLEXITY |
| **Date** | 2026-09-25 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 15/15 |

---

## Problem Statement

API Forge already produces explicit routing plans, but risk and task complexity do not yet jointly determine routing objectives, verification depth and execution composition through one canonical, explainable artifact. Runtime, CLI/TUI and governance need the same deterministic result so that higher-risk or more complex tasks receive proportionally stronger evidence and review without relying on providers, hidden heuristics or live external state.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Runtime supervisor | Plans and executes governed agentic tasks | Cannot yet translate risk and complexity into a single policy-controlled routing and verification plan |
| CLI/TUI operator | Inspects and operates local task execution | Needs to see why a plan was selected, which signals were used and what remains unresolved |
| Governance/review owner | Reviews evidence, gates and safe execution boundaries | Needs evidence-backed escalation and refusal behavior without recomputing a different routing decision |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Produce a versioned risk/complexity assessment from explicit local inputs and use it to derive routing objectives, gates, verification depth and execution composition |
| **MUST** | Preserve deterministic replay identity, evidence references, unresolved gaps, refusal details and policy provenance through `RoutingDecision` and `RoutingPlan` |
| **MUST** | Expose the same canonical assessment and derived decision to runtime, CLI/TUI and governance projections without provider calls or external mutation |
| **MUST** | Prove the behavior with existing and new golden, holdout, mutation and adversarial evaluation cases |
| **SHOULD** | Keep the assessment additive and compatible with existing `RoutingDecision/v1` and `RoutingPlan/v1` semantics |
| **COULD** | Provide explicit extension points for scorecard-adaptive routing (B) and graph-aware impact analysis (C), without activating either in the MVP |

**Priority Guide:**
- **MUST** = MVP fails without this (non-negotiable)
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes:

- [ ] **100%** of mandatory existing and new MVP evaluation cases pass the required gate.
- [ ] **100%** of replay runs using identical task input, evidence, policy version and ruleset produce the same assessment, decision, plan and projection digests.
- [ ] **100%** of paired risk/complexity cases defined for the MVP produce the expected policy-controlled change in gates, verification depth or specialist/reviewer composition.
- [ ] **0** evidence references or unresolved diagnostics are silently dropped between assessment, routing, projection and governance output.
- [ ] **100%** of MVP routing decisions remain local and offline, with no provider call, external mutation or implicit model dependency.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Deterministic replay | The same task, evidence, policy version and ruleset are provided twice | The risk/complexity classifier and routing pipeline run twice | Assessment, `RoutingDecision`, `RoutingPlan`, projections and stable digests are identical |
| AT-002 | Risk-sensitive policy | Two otherwise equivalent fixtures differ in their explicit task risk | The routing policy evaluates both requests | The expected objective order, gate state, verification depth or role composition changes according to local policy |
| AT-003 | Complexity-sensitive composition | Two fixtures differ only in an approved complexity input | The routing pipeline derives plans | The expected specialist, reviewer, critic/referee or verification composition changes deterministically |
| AT-004 | Unresolved evidence | A required evidence reference is unavailable or unresolved | The assessment and routing pipeline execute | The gap remains visible, the refusal/gate preserves `AF-*`, `field` and `unlock`, and no confident fallback hides the limitation |
| AT-005 | Canonical projection parity | A canonical assessment and derived plan exist | Runtime, CLI/TUI and governance projections render the result | Each surface reports the same selected roles, policy identity, evidence and unresolved items |
| AT-006 | Existing routing compatibility | An existing routing fixture does not use the new risk/complexity extension fields | The current local policy routes the task | Existing eligibility, deterministic tie-breaking, fallback and role semantics remain valid |
| AT-007 | Evaluation coverage | Existing golden, holdout, mutation and adversarial cases plus the new risk/complexity cases are registered | The runtime evaluation gate runs | Every mandatory kind is present, all required evidence is preserved, and the gate passes only on complete coverage |
| AT-008 | Offline safety boundary | The assessment is requested in the local MVP mode | The routing pipeline runs | No provider SDK, network call, external mutation or automatic approval is performed |

---

## Out of Scope

Explicitly NOT included in this feature:

- Historical scorecard inference as a required input to MVP risk or complexity classification; this is planned as B.
- Mandatory `ArchitectureGraph` impact analysis; this is planned as C.
- Provider/model-based classification, live external signals or hidden learned thresholds.
- Champion/challenger lifecycle, shadow routing and anti-starvation policy.
- External mutation, automatic approval, policy bypass or host-file mutation.
- Final operational design of B and C; each may receive a separate brainstorm and Define phase.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | The MVP must be offline-first and deterministic | Rules, thresholds, policy versions and tie-breakers must be local, explicit and replayable |
| Technical | Use the existing contracts and policy boundaries | The design should add an assessment boundary without silently replacing `RoutingDecision/v1` or `RoutingPlan/v1` |
| Evidence | Preserve evidence refs, unresolved state, provenance and refusal details | Missing or stale information must remain visible and may gate or escalate execution |
| Safety | No provider calls, external mutation or automatic approval from the assessment | The feature informs routing and gates but does not authorize unsafe actions |
| Compatibility | Existing routing fixtures and role semantics remain valid | Existing local behavior must remain covered by regression tests and evals |
| Scope | B and C are deferred extensions | The MVP must not require historical scorecards or graph completeness |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/contracts`, `src/apiforge/runtime`, `src/apiforge/rules`, `src/apiforge/cli_*`, `src/apiforge/tui`, `src/apiforge/surfaces`, plus `tests/` and `docs/contracts/` | Add the versioned assessment and deterministic policy path, integrate routing, and project one canonical result across surfaces |
| **KB Domains** | `genai`, `prompt-engineering`, `python`, `testing`, `data-quality` | Consult state machines, guardrails, typed validation, fixture/evaluation patterns and evidence-aware quality dimensions |
| **IaC Impact** | None | This is a local control-plane and policy evolution; no infrastructure or provider resource is required |

**Why This Matters:**

- **Location** → Design phase uses the existing contracts/runtime/policy structure and avoids misplaced implementation.
- **KB Domains** → Design phase can ground the assessment and eval strategy in the selected patterns.
- **IaC Impact** → No infrastructure planning is required for the MVP.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|-----------------|------------|
| A-001 | `TaskSpec` risk, preconditions and inputs can be normalized deterministically | A compatibility adapter or contract revision would be needed before classification | [x] Existing typed task and routing contracts support these inputs |
| A-002 | The local runtime policy file is the source of truth for objective order, gates and thresholds | A policy storage and freshness decision would be required before implementation | [x] Existing routing policy is loaded from versioned local YAML |
| A-003 | Existing `RoutingDecision/v1` and `RoutingPlan/v1` can carry the new assessment additively | A migration or new major contract would be required | [ ] Confirm during Design contract analysis |
| A-004 | Existing fixtures and eval gates can be extended with risk/complexity cases | A separate evaluation harness would be needed | [x] Current fixtures already cover routing replay and evidence-gated eval kinds |
| A-005 | The initial complexity feature set can be derived only from explicit local inputs | The MVP would need a new evidence source or would have to remain `Needs Clarification` | [ ] Define exact feature set during Design |
| A-006 | Runtime, CLI/TUI and governance can project one canonical assessment without recalculation | Surface parity would require a stronger shared projection contract | [ ] Confirm projection seam during Design |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | The gap between current routing plans and joint risk/complexity policy is explicit and actionable |
| Users | 3 | Runtime supervisor, CLI/TUI operator and governance owner are identified with distinct pain points |
| Goals | 3 | MUST/SHOULD/COULD goals define the MVP boundary and future extensions |
| Success | 3 | User-confirmed numeric targets cover mandatory evals, replay equality, expected differential cases, evidence preservation and offline safety |
| Scope | 3 | MVP responsibilities and B/C exclusions are explicit, including mutation and provider boundaries |
| **Total** | **15/15** | Clear enough to proceed to Design |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

No questions block Design. Design must resolve:

- The final name and fields of the additive risk/complexity assessment contract.
- The initial complexity feature set and exact policy thresholds.
- How the canonical assessment is attached to routing artifacts and projection payloads.
- The minimum new risk/complexity evaluation matrix and its evidence refs.
- The explicit extension seams for B scorecard-adaptive routing and C graph-aware impact analysis.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-25 | define-agent | Converted the confirmed BRAINSTORM into requirements with a 15/15 clarity score and measurable MVP gates |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_RISK_AWARE_ROUTING_TASK_COMPLEXITY.md`
