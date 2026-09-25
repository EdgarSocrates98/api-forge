# BRAINSTORM: Risk-Aware Routing and Task Complexity

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | RISK_AWARE_ROUTING_TASK_COMPLEXITY |
| **Date** | 2026-09-25 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |

---

## Initial Idea

**Raw Input:** Evolve the next API Forge opportunity from the post-wave routing review in `prompt_evo_proxima_oportunidade.md`, prioritizing risk-aware routing objectives and a task-complexity model while preserving deterministic, offline-first execution. Scorecard-driven routing and graph-aware impact analysis are planned as later extensions and may receive separate brainstorm sessions.

**Context Gathered:**
- The current platform already has explicit `RoutingDecision` and `RoutingPlan` contracts with primary, fallback, parallel, reviewer, critic and referee roles.
- Routing already preserves evidence, unresolved states, freshness-aware signals, expertise eligibility, deterministic tie-breaking and bounded execution modes.
- The current policy emphasizes efficiency and quality, with security represented primarily as an eligibility gate; task complexity is not yet a first-class routing input.
- Existing fixtures and tests cover deterministic replay, safety eligibility, routing-plan role separation, scorecard freshness, evidence gates, mutation and adversarial cases.
- The supplied evolution review identifies risk-aware objectives, task complexity and graph-aware impact as the next strategic connection point after the completed adaptive-routing waves.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/contracts`, `src/apiforge/runtime`, `src/apiforge/rules`, `src/apiforge/cli_*`, `src/apiforge/tui`, `src/apiforge/surfaces` | Add one versioned assessment contract, deterministic policy evaluation, routing integration and read-only projections from the canonical result |
| Relevant KB Domains | `genai`, `prompt-engineering`, `python`, `testing`, `data-quality` | Use state-machine/guardrail boundaries, typed validation, fixture-driven tests, evaluation gates and evidence-aware quality dimensions |
| IaC Patterns | N/A; this is a local control-plane and policy evolution | Keep the MVP offline-first and policy-file driven; no infrastructure or provider dependency is required |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | What opportunity should be the focus? | Risk-aware routing plus task complexity; scorecard and graph work remain later extensions | Defines a focused vertical slice instead of reopening the completed routing waves |
| 2 | Who is the primary consumer? | Runtime, CLI/TUI and governance all need the result from the MVP | Requires one canonical decision artifact with consistent projections rather than separate interpretations |
| 3 | Which constraint dominates? | Determinism and offline reproducibility | Rules, thresholds, policy versions and evidence must be local, explicit and replayable |
| 4 | What defines success? | Deterministic replay, risk-sensitive behavior and a verifiable change in specialist/verification composition | Eval fixtures must prove both stable output and meaningful policy-driven plan changes |
| 5 | Which samples should ground the design? | Existing repository fixtures and tests only | The initial contract and evals must be derived from local routing, evolution, adaptive-routing and runtime evidence |

**Minimum Questions:** 3 (to ensure clarity before proceeding)

---

## Sample Data Inventory

> Samples improve LLM accuracy through in-context learning and few-shot prompting.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/agentic_runtime/routing_cases.yaml`; `tests/fixtures/agentic_runtime/evolution_cases.yaml` | Present | Covers observed efficiency, unknown signals, safety gating, local/replay/shadow modes and blocked external-read evidence |
| Output examples | `tests/runtime/test_routing.py`; `tests/runtime/test_routing_plan.py`; `docs/contracts/RoutingDecision-v1.md`; `docs/contracts/RoutingPlan-v1.md` | Present | Shows current decision fields, role separation, deterministic IDs, fallback behavior and explainable rejection data |
| Ground truth | `tests/evals/cases/adaptive_routing.yaml`; `tests/evals/test_adaptive_routing_gate.py` | Present | Golden, holdout, mutation and adversarial expectations define pass/block behavior and evidence requirements |
| Related code | `src/apiforge/contracts/routing.py`; `src/apiforge/runtime/routing.py`; `src/apiforge/rules/agentic_runtime.yaml`; `src/apiforge/runtime/policy.py` | Present | Reuse typed contracts, policy loading, eligibility, ranking, evidence handling and governance gates |

**How samples will be used:**

- Define deterministic risk/complexity input combinations and their expected policy outcomes.
- Extend replay fixtures without replacing the current routing contract or role semantics.
- Prove that changing risk or complexity changes gates, reviewers, critic/referee participation or verification requirements when policy says it should.
- Preserve the existing golden/holdout/mutation/adversarial evaluation boundary.
- Use current rejection and unresolved formats as the reference for safe failure behavior.

---

## Approaches Explored

### Approach A: Deterministic Policy Compiler ⭐ Recommended

**Description:** Add a versioned risk/complexity assessment produced from explicit task, evidence, expertise and policy inputs. The assessment feeds `RoutingRequest`, `RoutingDecision` and `RoutingPlan`, while runtime, CLI/TUI and governance project the same canonical artifact.

**Pros:**
- Directly matches the existing routing contracts and policy loader.
- Provides deterministic replay and stable explainability.
- Keeps unknown and unresolved evidence visible.
- Limits MVP changes to local contracts, rules, runtime integration, projections and evals.

**Cons:**
- Initial complexity rules require deliberate calibration.
- The first classifier may be coarse until historical scorecards and graph evidence are added.

**Why Recommended:** The codebase already has the required seams in `contracts/routing.py`, `runtime/routing.py`, `rules/agentic_runtime.yaml` and the routing/evaluation fixtures. The KB patterns for typed validation, state-machine boundaries, guardrails and evaluation frameworks reinforce a versioned, evidence-gated policy compiler. Evidence confidence: strong — KB pattern plus direct codebase match.

---

### Approach B: Scorecard and Historical Evidence First

**Description:** Infer risk/complexity from scorecards, freshness, eval outcomes and historical execution observations, then use those signals to alter ranking, reviewers and verification.

**Pros:**
- Builds on the existing multidimensional scorecard and freshness model.
- Can improve decisions as verified history accumulates.
- Provides richer comparisons between capability implementations.

**Cons:**
- Introduces feedback bias and starvation risk for new candidates.
- Depends more heavily on fresh, complete observations.
- Makes replay depend on historical state unless snapshots are tightly versioned.

**Why not recommended for the MVP:** The evolution review already identifies challenger/champion lifecycle and shadow routing as follow-up work. Those safeguards should precede scorecard-driven classification. This becomes the planned B extension.

---

### Approach C: Graph-Aware Impact Classifier

**Description:** Use `WorkspaceManifest`, `ProjectManifest`, `ContextScope` and `ArchitectureGraph` relations to derive impact breadth and complexity before applying risk-aware routing policy.

**Pros:**
- Connects workspace context, impact, expertise and governance.
- Fits the multi-repository foundation already present.
- Is the strongest long-term path for architecture-change tasks.

**Cons:**
- Requires graph completeness and freshness evidence.
- Unknown relationships can make classification conservative or blocked.
- Expands the MVP beyond the core routing-policy problem.

**Why not recommended for the MVP:** The graph foundation exists, but making it mandatory would introduce a new evidence dependency before the deterministic policy boundary is proven. This becomes the planned C extension.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A for the MVP, with explicit extension points for Approach B and Approach C |
| **User Confirmation** | 2026-09-25 — explicitly confirmed after approach comparison and two validation checkpoints |
| **Reasoning** | Start with the smallest deterministic boundary that connects risk, complexity, routing plans, verification and all three consumer surfaces. Develop B and C afterward, potentially through separate brainstorms, without allowing them to change MVP replay semantics. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Introduce one canonical risk/complexity assessment before routing-plan derivation | Prevents runtime, CLI/TUI and governance from calculating different interpretations | Separate per-surface classifiers |
| 2 | Keep rules, thresholds and objective order in versioned local policy | Makes decisions replayable and reviewable offline | Hardcoded or provider-dependent heuristics |
| 3 | Preserve unresolved evidence and explicit refusal details | The platform must not turn missing evidence into a confident routing result | Silent fallback to a default confidence or agent |
| 4 | Keep scorecard inference and graph impact as later extensions | Applies YAGNI while preserving the strategic roadmap | Making historical scorecards or graph completeness an MVP prerequisite |
| 5 | Reuse existing fixtures and eval gates | Maintains continuity with the completed adaptive-routing work | Introducing external traces or provider samples for the first contract |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Scorecard-driven risk/complexity inference in the MVP | Historical feedback is valuable but needs challenger/shadow safeguards to avoid bias and starvation | Yes — planned B, with a separate brainstorm if needed |
| Mandatory graph-aware impact analysis | The workspace graph is a strong foundation but would add an evidence dependency before the policy boundary is validated | Yes — planned C, with a separate brainstorm if needed |
| Provider or model-based task classification | Violates the selected offline/replayable constraint and would weaken deterministic evidence provenance | Only as an explicitly governed future adapter, not as an implicit classifier |
| Automatic external mutation or policy override from the new assessment | The MVP needs to inform routing and gates, not authorize mutations | Yes, only behind existing approval and policy boundaries |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept | ✅ | Confirmed with “ok” | No |
| Component breakdown | ✅ | Confirmed with “ok” | No |
| Data flow | ✅ | Canonical assessment → routing plan → runtime/CLI-TUI/governance projections was accepted as the intended flow | No |
| Error handling | ✅ | Unresolved evidence remains explicit and policy-controlled; no silent confidence fallback | No |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

API Forge can already select and execute explicit routing plans, but its policy does not yet make task complexity and risk jointly determine objectives, verification depth and execution composition in one deterministic, explainable artifact.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Runtime supervisor | Needs a stable way to translate task risk and complexity into routing roles, verification depth and safe gates |
| CLI/TUI operator | Needs to understand why a plan was selected, which signals were used and what remains unresolved |
| Governance/review owner | Needs evidence-backed policy decisions that can block or escalate high-risk work without recomputing runtime behavior |

### Success Criteria (Draft)

- [ ] Replaying the same task, evidence, policy version and ruleset reproduces the same assessment, decision, plan and projections.
- [ ] Changing a task's risk or complexity inputs produces a policy-controlled change in gates, verification depth or specialist/reviewer composition.
- [ ] The assessment preserves evidence references, policy identity, rule provenance and unresolved gaps.
- [ ] Existing golden, holdout, mutation and adversarial evals remain green, with new cases proving risk sensitivity and complexity impact.
- [ ] Runtime, CLI/TUI and governance consume the same canonical assessment without provider calls or external mutation.

### Constraints Identified

- Offline-first and deterministic; no implicit model, provider, network or live workspace dependency.
- Rules and thresholds must be versioned policy data with stable tie-breaking and replay identity.
- Existing `RoutingDecision/v1` and `RoutingPlan/v1` semantics remain compatible unless a separately approved additive contract is required.
- Critical evidence, refusal codes, unresolved gaps and policy limitations must remain visible.
- B and C are intentionally deferred from the MVP and should be treated as separate future design slices.
- Unresolved for `/define`: final contract name and fields, the initial complexity feature set, exact policy thresholds, projection layout and the minimum new eval matrix.

### Out of Scope (Confirmed)

- Historical scorecard inference as a required input to MVP classification.
- Mandatory `ArchitectureGraph` impact analysis.
- Provider/model-based classification or live external signals.
- External mutation, automatic approval or policy bypass.
- Champion/challenger lifecycle and shadow-routing behavior.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 discovery questions, including sample collection |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 4 |
| Validations Completed | 2 checkpoints confirmed by the user |
| Duration | Not measured; interactive session |
| Unresolved gaps | Threshold calibration, final contract shape, projection details and expanded eval matrix remain for `/define` |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_RISK_AWARE_ROUTING_TASK_COMPLEXITY.md`

After A reaches the build/verification boundary, start a separate brainstorm for B (scorecard-adaptive routing) and C (graph-aware impact analysis) if their requirements are not yet sufficiently clear.
