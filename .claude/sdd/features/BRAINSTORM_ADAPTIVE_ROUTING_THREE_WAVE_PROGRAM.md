# BRAINSTORM: Adaptive Routing Three-Wave Program

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM` |
| **Date** | 2026-09-24 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |

---

## Initial Idea

**Raw Input:** `prompt_evo_melhor_avaliacao.md`, followed by the user's request
to close Wave 1, continue automatically through Wave 2 and Wave 3, commit each
wave, then push and open/update a pull request.

**Context Gathered:**

- The runtime already has deterministic capability eligibility, ranking,
  scorecards, evidence coverage and promotion gates.
- `RoutingDecision` contains `selected` and `fallback_order`, while the
  supervisor currently materializes the ordered candidates as invocations;
  this leaves primary, fallback, parallel review and criticism semantically
  ambiguous.
- `RoutingPolicy` currently orders efficiency and quality, the evolution policy
  keeps adaptive plans disabled, and the eval gate is evidence-gated through
  golden, holdout and mutation evidence.
- The component model separates Agent (execution), Skill (capability), Command
  (entrypoint) and KB (source of truth), which supports a later expertise-pack
  wave without putting methodology into agent profiles.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/contracts/`, `runtime/`, `capabilities/`, `evals/`, `rules/` | Add versioned contracts and deterministic services; keep the supervisor as the authorization boundary |
| Relevant KB Domains | `genai`, `prompt-engineering`, `testing`, `pydantic`, shared `component-model` | Use explicit state machines, structured outputs, evidence-backed evals and thin agent/skill/KB layers |
| IaC Patterns | No infrastructure mutation is required; host integrations remain read-only or policy-gated | Keep all waves local, replayable and bounded; do not add provider access |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | What is the primary goal? | Build one program covering RoutingPlan, scorecards/evals and expertise packs, delivered in incremental waves | The brainstorm is a program with a staged contract boundary, not an isolated routing tweak |
| 2 | Who is the priority user? | All users equally: maintainers, agent/skill authors and operators | Every wave must expose deterministic behavior, authoring boundaries and operator-readable evidence |
| 3 | Which constraints are non-negotiable? | Offline/hostless operation, backward compatibility, and deterministic execution budgets | New contracts must be additive, local-first and bounded; network or admin access cannot be required |
| 4 | Which samples are available? | Repository fixtures/tests/evals, routing/scorecard traces when available, and reviewed golden/holdout/mutation/adversarial examples | Existing fixtures become regression inputs; observed traces stay optional evidence and never become fabricated defaults |

**Minimum Questions:** 3 (to ensure clarity before proceeding)

---

## Sample Data Inventory

> Samples improve LLM accuracy through in-context learning and few-shot prompting.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `src/apiforge/contracts/routing.py`, `runtime/routing.py`, `runtime/supervisor.py`, `rules/agentic_runtime.yaml` | available | Current contracts, policy and execution seams |
| Output examples | `tests/runtime/test_routing.py`, `test_supervisor.py`, `test_promotion.py`, `test_feedback.py` | available | Existing deterministic routing and evidence assertions |
| Ground truth | `tests/evals/`, `tests/runtime/`, `tests/fixtures/` | available | Golden, holdout, mutation and fixture-backed behavior |
| Related code | `src/apiforge/capabilities/scorecard.py`, `runtime/promotion.py`, `runtime/evidence_gate.py`, `contracts/agentic.py` | available | Reusable scorecard, gate and profile patterns |

**How samples will be used:**

- Preserve current routing and supervisor behavior as compatibility fixtures.
- Add contract examples for primary/fallback/parallel/reviewer execution.
- Use evidence-backed eval records to promote scorecard signals.
- Use adversarial and stale-signal cases to prevent unsafe promotion.
- Use profile and knowledge-pack examples to test capability matching without
  requiring live hosts or model calls.

---

## Approaches Explored

### Approach A: Staged execution-plan program ⭐ Recommended

**Description:** Deliver a bounded program in waves: first introduce
`RoutingPlan/v1` and correct execution semantics; then add multidimensional
scorecards, freshness and adversarial evaluation; finally add expertise packs
and multiple implementations per capability.

**Pros:**

- Fixes the current primary/fallback ambiguity before expanding the candidate
  space.
- Preserves existing contracts through additive migration and replay.
- Gives every wave a separate validation and commit boundary.
- Matches the existing GenAI state-machine and component-model patterns.

**Cons:**

- The full benefit arrives progressively rather than in one release.
- Later waves must consume stable contracts from earlier waves.

**Why Recommended:** The repository already has the seams for all three
concerns, but `RoutingPlan` is the safest first boundary. It makes the
supervisor behavior explicit before scorecards and knowledge packs increase
the number of candidates.

---

### Approach B: Evidence and scorecards first

**Description:** Start with multidimensional scorecards, signal freshness,
adversarial evals and poisoning protection; add `RoutingPlan` and expertise
packs afterward.

**Pros:**

- Improves the quality of ranking inputs immediately.
- Establishes strong promotion evidence before adaptive execution.

**Cons:**

- Leaves `fallback_order` execution semantics ambiguous for longer.
- The supervisor still lacks an explicit distinction between fallback and
  parallel review.

---

### Approach C: Expertise packs first

**Description:** Separate agents, skills and knowledge packs first, allowing
multiple implementations for each capability before evolving scorecards and
execution planning.

**Pros:**

- Directly exercises the component model and knowledge architecture.
- Creates a richer candidate pool for later routing comparisons.

**Cons:**

- Expands the catalog before execution semantics are explicit.
- Makes it harder to distinguish fallback, reviewer, critic and referee roles.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — staged execution-plan program |
| **User Confirmation** | 2026-09-24 |
| **Reasoning** | The user selected the staged program and explicitly authorized automatic progression through all waves, with one commit after each wave and push/PR after the final wave |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Wave 1 starts with `RoutingPlan/v1` and explicit execution roles | Resolve the semantic difference between primary, fallback, parallel and review before increasing candidate diversity | Scorecard-first and expertise-first sequencing |
| 2 | Waves 2 and 3 must complete automatically after the prior wave validates | User requested no manual pause between waves and no unfinished wave | Stopping after each wave for confirmation |
| 3 | Every wave has its own commit and verification boundary | Makes progress reversible and preserves evidence for each contract transition | One large combined commit |
| 4 | Existing CLI/MCP/contracts remain compatible | The user selected backward compatibility as a non-negotiable constraint | Breaking migration to new contracts |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Multidimensional scorecards in Wave 1 | It does not solve the first execution-plan ambiguity and would widen the first contract | Yes, Wave 2 |
| Expertise packs in Wave 1 | It expands candidate discovery before roles and fallback semantics stabilize | Yes, Wave 3 |
| Full task complexity and repository-relation inference | Requires broader evidence and is not necessary to establish the staged routing boundary | Yes |
| Autonomous `ask`, `improve`, `migrate` and `fix` orchestration | Previously deferred after ship and outside this routing evolution program | Yes, later roadmap |
| Auto-update, remote knowledge synchronization, symlink installation and host overwrite | Security and ownership boundaries are not prerequisites for the three routing waves | Yes, later roadmap |
| Distributed workspace debate and total host parity | Requires external coordination and broader host evidence | Yes, later roadmap |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Program approaches | ✅ | User selected Approach A, staged across all waves | Yes — program became execution-plan first |
| YAGNI Wave 1 scope | ✅ | User authorized automatic progression through Waves 1, 2 and 3 | Yes — no manual pause between validated waves |
| Compatibility and safety constraints | ✅ | User required offline/hostless use, backward compatibility and deterministic budgets | Yes — all contracts and policies remain additive and bounded |
| Implementation checkpoints | ✅ | User required a commit after each wave and push/PR after Wave 3 | Yes — commits become explicit verification boundaries |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

API Forge needs a backward-compatible, offline-first evolution path that turns
capability routing into an explicit execution plan, strengthens evidence-backed
evaluation, and separates reusable expertise from agent identity without
weakening safety gates.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Runtime maintainers | Primary, fallback and parallel execution semantics are mixed in the current routing order |
| Agent and skill authors | Capability identity, methodology and knowledge are not yet fully separated for multiple implementations |
| Operators and reviewers | Ranking quality, evidence freshness and promotion state need clearer explanations |

### Success Criteria (Draft)

- [ ] Existing routing requests remain readable and replayable after each wave.
- [ ] The supervisor executes a typed plan with explicit primary, fallback and review semantics.
- [ ] Scorecard promotion distinguishes observed, stale, unknown and unresolved signals and requires adversarial evidence where policy declares it.
- [ ] Expertise packs can be attached to capabilities without moving methodology into agent profiles.
- [ ] Every wave has focused tests, release-gate evidence and a separate commit.
- [ ] No wave requires network access, provider credentials, administrative installation or external mutation from the core.

### Constraints Identified

- Offline-first and hostless operation remain valid.
- Existing contracts, CLI, MCP and receipts must remain compatible.
- All adaptive behavior is deterministic, bounded and evidence-gated.
- External mutation remains outside the core and under the existing host boundary.

### Out of Scope (Confirmed)

- Autonomous high-level `ask`, `improve`, `migrate` and `fix` orchestration.
- Complete relation inference across all repository types.
- Separate `apiforge here` command.
- Auto-update and remote knowledge-pack synchronization.
- Symlink installation and automatic host-file overwrite.
- Full task-level precedence before manifests stabilize.
- Distributed workspace debate and a promise of total host parity.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | Four discovery questions plus the sample-data question |
| Approaches Explored | Three |
| Features Removed (YAGNI) | Seven deferred groups |
| Validations Completed | Four checkpoints |
| Duration | Same working session |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM.md`
