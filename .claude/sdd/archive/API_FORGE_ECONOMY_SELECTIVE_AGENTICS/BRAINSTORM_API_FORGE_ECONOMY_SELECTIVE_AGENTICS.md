# BRAINSTORM: API Forge Economy — Selective Agentics (Onda 4)

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_SELECTIVE_AGENTICS |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** `prompt_evo_economy.md` Wave 4 — lazy expertise (§26–27), capability-first (§28), anti-agentic-theater gate (§29), bounded debate on a shared capsule with position deltas (§30–32), economic champion/challenger with a shadow budget (§36–38), contract-first agent communication and hierarchical synthesis (§84–85), subagents that receive a minimum capsule instead of the parent context (§86) and context budgets per role (§87).

**Context Gathered:**
- `runtime/supervisor.py::execute_run`: every invocation gets `input_refs=spec.inputs` and the same generic prompt — no role-specific context, no capsule.
- `runtime/adapters.py::AgentRequest` (`extra=forbid`): prompt, input_refs, tool_names, output_contract.
- `knowledge/loader.py`: 38 local packs (~220 KB), each with `areas`, `rule_ids`, `summary`; `Pack.as_expertise_pack()` projects to `ExpertisePack/v1`. Routing already refuses missing required packs, but nothing *selects* packs from an intent.
- `rules/agentic_runtime.yaml`: 8 runtime capabilities (5 specialists, reviewer, critic, referee); `agents/*.md`: 53 agent docs with `rule_areas` and `executors` frontmatter.
- `debate/service.py`: `submit(side, position, evidence)` stores free text; `close()` gives the referee everything.
- `runtime/economy.py::apply_economy`: challenger slots trimmed per envelope, but challengers are never executed; no shadow budget.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `knowledge/selector.py`, `runtime/role_context.py`, `runtime/shadow.py`, `debate/packet.py`, `agentops/agent_audit.py`, `contracts/selective.py`, rules YAML | Reuse gateway capsule + ledger |
| Relevant KB Domains | pydantic, testing, genai multi-agent | Contracts, deterministic evals |
| IaC Patterns | N/A | Offline, no provider SDK |

---

## Discovery Questions & Answers

> Autonomous mandate; answers from the prompt and codebase evidence.

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | How are packs chosen without an LLM? | Declarative triggers (`rules/expertise_triggers.yaml`): intent keywords, frameworks, fact kinds, capabilities → pack domains; no trigger → `unresolved`, never "load all" | Deterministic, auditable selection |
| 2 | What does each role receive (§86–87)? | `RoleContextPlan/v1`: primary=focused (contract/schema/code/test refs), reviewer=evidence_plus_delta, critic=decision_plus_evidence, referee=disagreements_only; per-role byte share of the envelope `context_bytes` | Supervisor passes role refs; bytes attributed in ledger |
| 3 | Where does the capsule come from inside a run? | TaskSpec inputs `target=<METHOD> /path` (or `graph_target=operation:...`) + `case=<dir>` (default `.apiforge/case`); no target → roles get refs of task inputs only and `capsule-unavailable` is recorded | No silent full-context fallback |
| 4 | How is debate made economical? | `PositionDelta/v1` (position, evidence, disagreements, risks, confidence) on `debate submit`; `debate packet` builds the referee input = capsule id + deduped deltas + disagreement set; bytes compared to naive replication | Referee reads deltas, not essays |
| 5 | How does shadow stay bounded (§38)? | Envelope `shadow_share` per profile; deterministic sampling by run id hash; a sampled challenger runs only from calls left after the verification reserve, and its artifact never enters the result | Learning without paying for it every run |
| 6 | What is the agentic-theater gate (§29)? | `agents audit`: per agent, unique capability / expertise (rule areas) / validator-tool (executors) / decision role; all false → `merge-candidate` with overlapping agents | Report only, no deletion |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `knowledge/*/pack.yaml` | 38 | Areas, rule ids, summaries |
| Input files | `agents/*.md` | 53 | `rule_areas`, `executors` frontmatter |
| Input files | `tests/fixtures/economy_payments` | 1 | Capsule source for role context |
| Ground truth | `evals/corpus/selective-agentics/*.yaml` (to create) | ~12 | intent → expected packs; role byte ceilings; debate packets |
| Related code | `runtime/supervisor.py`, `debate/service.py`, `runtime/economy.py` | — | Integration points |

---

## Approaches Explored

### Approach A: Deterministic role-context layer on top of the existing runtime ⭐ Recommended

**Description:** Add selector, role context planner, position deltas/referee packet, shadow sampler and agent audit as separate deterministic modules; the supervisor only asks the planner for each invocation's refs and records them.

**Pros:** no change to routing decisions; measurable bytes per role; each piece testable alone.
**Cons:** real savings depend on hosts honoring `context_refs` (fake adapter only records them).

**Why Recommended:** fits the existing assessment/plan pattern (confidence 0.90).

### Approach B: New orchestrator with role prompts

**Description:** Replace `execute_run` invocation building with a prompt compiler per role.
**Cons:** parallel orchestrator — explicitly rejected by §12.

### Approach C: LLM summarization for referee input

**Cons:** pays tokens to save tokens (§9).

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28 — pre-approved autonomous delivery |
| **Reasoning** | Deterministic, additive, measurable |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | No trigger → zero packs + `unresolved` | Lazy by default, never "load all" | Loading all packs on uncertainty |
| 2 | Role refs are a subset of one shared capsule | One capsule per run (§31) | Per-role capsule rebuilds |
| 3 | Shadow artifacts never enter the result or the gate | Shadow learns, never decides (§37) | Blending challenger output |
| 4 | Agent audit is report-only | Removal is a human decision | Auto-pruning agents |
| 5 | `AgentRequest.context_class/context_refs` optional | Adapters that ignore them keep working | Rewriting `input_refs` (breaks replay digests) |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Deterministic implementation per capability (`contract.compatibility.rest`) | Wave 3 L0 stop already answers deterministic-first; capability catalog has `implementation` | Yes |
| Reviewer ROI / information gain learning | Belongs to Wave 6 (needs observed scorecards) | Yes |
| Prompt compiler / stable prefixes | Extras wave (§81–83) | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Role context classes and budgets | ✅ | Autonomous mandate; matches §87 table | No |
| Debate packet + shadow budget | ✅ | Autonomous mandate | Yes — shadow limited to calls after reserve |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
Every runtime role receives the same full task inputs, packs are never selected from intent, debates replicate full positions to the referee, challengers are planned but never measured, and nothing flags agents that add no unique capability.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Agent host | Each subagent inherits the parent context |
| Maintainer | Cannot tell which agents are redundant or whether challengers pay off |

### Success Criteria (Draft)
- [ ] Expertise selection precision/recall 1.0 on the corpus; no-trigger intents select 0 packs.
- [ ] Role context bytes: reviewer/critic/referee each ≤ primary and total ≤ 60% of naive replication.
- [ ] Referee packet ≥ 50% smaller than naive with every evidence id preserved.
- [ ] Shadow sampling frequency within ±2 pp of `shadow_share` over 1000 synthetic runs; shadow never changes final status.
- [ ] Agent audit deterministic; every agent has a verdict.

### Constraints Identified
- Offline, no provider SDK; AF codes cataloged; routing decisions unchanged.

### Out of Scope (Confirmed)
- Reviewer ROI learning, prompt compiler, auto agent removal.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 6 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 3 |
| Validations Completed | 2 |
| Duration | ~15 min |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_SELECTIVE_AGENTICS.md`
