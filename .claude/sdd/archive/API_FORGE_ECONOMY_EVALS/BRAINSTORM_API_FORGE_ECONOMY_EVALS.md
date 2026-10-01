# BRAINSTORM: API Forge Economy — Economy Evals (Onda 6)

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EVALS |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** `prompt_evo_economy.md` Wave 6 — separate quality/evidence/cost/latency/context axes instead of a blended score (§72), a canonical task × profile matrix (§73–75), an evaluation gate that ships an optimization only with zero safety regression (§76), a replay corpus that re-evaluates stored runs under new policy without providers (§77–78), multi-agent ROI (§79), information-gain stopping (§80) and quality-floor ranking where quality is a constraint and cost the optimization (§34–35).

**Context Gathered:**
- Per-wave evals exist (`evals economy`, `economy-routing`, `cache`, `selective-agentics`, `tool-economy`), each with its own gates; nothing compares profiles on the same canonical tasks with correctness as an axis.
- `openapi/diff.py::diff_contracts` classifies breaking changes deterministically; `tests/fixtures/openapi/orders-v1.yaml` / `orders-v2-breaking.yaml`, `tests/fixtures/grpc/orders*.proto`.
- Runs persist `routing.json`, `routing-plan.json`, `economy.json`, `summary.json`, artifacts under `.apiforge/tasks/<task>/runs/<run>` — enough for replay.
- `ScorecardRoutingPolicy.min_quality_score` demotes low-quality candidates to the challenger lane (still competing); champions keep inherited order, ignoring `observed_cost`.
- Escalation already triggers only on low confidence / unresolved / disagreement; the "why not escalate" is not reported.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `evals/matrix.py`, `evals/gate.py`, `evals/replay.py`, `economy/roi.py`, `runtime/information_gain.py`, `runtime/scorecard_routing.py` | Reuse runtime + diff |
| Relevant KB Domains | testing | Holdout/mutation |
| IaC Patterns | N/A | Offline |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | What is "correctness" offline? | Deterministic verdict (breaking / compatible) of each canonical contract pair vs ground truth, plus the safety invariant (risk-required roles present) | Quality axis without an LLM |
| 2 | How are axes combined? | They are not — each axis gated separately; no blended score | §72 |
| 3 | Holdout and mutation? | Cases flagged `holdout` reported separately and gated; mutants (required-field removal, path removal, enum narrowing) injected into compatible candidates must flip the verdict | Mutation score |
| 4 | What does replay compare? | Stored decision → rebuilt pre-economy plan → current policy → diff vs stored economy (roles, call cap, trims); removed risk-required roles must be 0 | Policy change safety without providers |
| 5 | ROI measurement? | Per non-primary role from stored runs: calls, facts/unresolved added beyond the primary, outcome changed | Evidence for trimming |
| 6 | Quality floor? | Optional `quality_floor` on the scorecard policy: below floor → excluded (`quality-below-floor`); champions ordered by observed cost when the floor is set | §34–35 without changing defaults |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `evals/corpus/economy-matrix/*.yaml` (to create) | 16 tasks | inline baseline/candidate OpenAPI + 2 gRPC |
| Ground truth | same (`expected: breaking|compatible`, `holdout`) | 16 | |
| Replay | `evals/corpus/economy-replay/` (generated runs) | 3 | stored run artifacts |
| Related code | `openapi/diff.py`, `grpc` compatibility, `runtime/runner.py` | — | |

---

## Approaches Explored

### Approach A: Deterministic matrix over canonical contract tasks ⭐ Recommended

**Description:** Each task → deterministic verdict (L0) + runtime run per profile (fake adapter) → five separate axes; gate/replay/ROI read reports and stored runs.
**Pros:** Offline, reproducible, correctness grounded in the diff engine.
**Cons:** Agent reasoning quality not measured (no model) — reported as out of scope.

### Approach B: LLM-judged quality

**Cons:** Needs providers; nondeterministic; §16 (never invent).

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28 — pre-approved |
| **Reasoning** | Measurable offline |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | No blended score | §72 | weighted sum |
| 2 | Gate rejects any safety regression regardless of savings | §76 | tolerance on safety |
| 3 | Quality floor opt-in | Defaults unchanged | forcing floor on existing routing |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Real API corpus from external repos | Offline fixtures only | Yes |
| Monetary cost axis | Only with explicit pricing (§16) | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Matrix axes | ✅ | Autonomous mandate | No |
| Gate/replay/ROI | ✅ | Autonomous mandate | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
No eval compares profiles on the same canonical tasks with correctness, evidence, cost, context and latency as separate axes, and no gate, replay or ROI protects future economy optimizations.

### Success Criteria (Draft)
- [ ] 16 tasks × 3 profiles; correctness 1.0 in every profile; safety invariant regressions 0.
- [ ] Mutation score 1.0; holdout pass.
- [ ] Gate rejects a synthetic regression and accepts an identical report.
- [ ] Replay: 0 removed risk-required roles.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 6 |
| Approaches Explored | 2 |
| Features Removed (YAGNI) | 2 |
| Validations Completed | 2 |
| Duration | ~10 min |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_EVALS.md`
