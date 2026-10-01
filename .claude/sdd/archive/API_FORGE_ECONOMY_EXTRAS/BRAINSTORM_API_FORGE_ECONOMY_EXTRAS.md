# BRAINSTORM: API Forge Economy — Verification, Retrieval, Evidence and Providers (Onda 7)

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EXTRAS |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** remaining sections of `prompt_evo_economy.md` after waves 0–6: test selection by impact and the V0–V5 verification ladder (§45–46), workspace locality-first (§48–49), `doctor --economy` (§55), deterministic query expansion, retrieval ranking and progressive retrieval (§56–58), evidence graph with `evidence://` (§60), provider-agnostic capability descriptor and model tiering with an optional local tier (§61–63), stable prompt prefix and canonical serialization (§81–83).

**Context Gathered:**
- Cache selections record test refs and dependency files (wave 2); `context delta` maps changed files to operations — enough to select tests without running anything.
- Workspace graph (`workspace/graph.py`) has declared `contains`/`depends_on` relations between repositories.
- `apiforge doctor` inspects installation/runtime; no economy checks.
- Knowledge packs: 38 domains × 8 markdown files; `knowledge select` picks packs, not passages.
- Case graph (`graph/build.py`) links operations, facts, findings and rules — `evidence://` can resolve one hop at a time.
- `AgentRequest.prompt` is a short dynamic string; no stable prefix; no provider descriptor.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `verification/selection.py`, `workspace/locality.py`, `economy/doctor.py`, `knowledge/retrieval.py`, `evidence/resolve.py`, `economy/providers.py`, `runtime/prompting.py`, rules YAML | Additive |
| Relevant KB Domains | testing, python | Deterministic |
| IaC Patterns | N/A | Offline |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Does test selection run tests? | No — `verify plan` outputs `VerificationPlan/v1` (ladder level by risk, selected tests with reasons, commands); execution stays with the host/CI | Read-only |
| 2 | Ladder by what? | Risk class (micro/low/medium/high from `sdd classify`) → V1/V2/V4/V5; breaking contract change forces ≥ V4 | Never V5 for everything, never below the risk floor |
| 3 | Retrieval without embeddings? | Passages = markdown sections of selected packs; rank by expanded-term hits, heading match, pack trigger reason and freshness; tiers top-3 → top-5 → rest | Progressive, deterministic |
| 4 | `evidence://` scope? | `evidence://{finding|fact|rule|operation}/<id>` → node + one-hop neighbors + ctx ref of its source; the chain is walked on demand | No full chain dumps |
| 5 | Provider tiering without providers? | Declared `ProviderCapability/v1` table; tier choice T0–T3 from deterministic availability, risk and benchmark evidence (scorecards); no evidence → no downgrade | Never "cheap model = enough" by assumption |
| 6 | Stable prefix? | `PromptEnvelope/v1`: prefix = protocol + capability contract + expertise pack versions (canonical, hashed), suffix = capsule id + refs + task; request carries `prompt_prefix_sha256` | Cache-friendly across runs |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/economy_payments`, `tests/fixtures/workspaces` | 2 | tests, workspace relations |
| Ground truth | `evals/corpus/economy-extras/*.yaml` (to create) | ~10 | selection, retrieval, evidence, tiers |

---

## Approaches Explored

### Approach A: Seven small deterministic modules behind verbs ⭐ Recommended
**Pros:** each independently testable; no core behavior change. **Cons:** breadth.

### Approach B: Fold into existing verbs (e.g. `context capsule --tests`)
**Cons:** overloads contracts shipped in waves 1–2.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28 — pre-approved |
| **Reasoning** | Additive, measurable |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Verification plan never executes | Mutation/execution boundary stays with CI | running pytest from core |
| 2 | No evidence → keep strong tier | §62 prove per task family | defaulting to cheap tier |
| 3 | Prefix hash, not provider cache control | Provider-agnostic core (§61) | provider-specific cache headers |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Embedding/semantic ranking | Optional per §57; deterministic first | Yes |
| Running a local model | §63 optional; core must not depend on it | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Verification + retrieval | ✅ | Autonomous mandate | No |
| Evidence + providers + prefix | ✅ | Autonomous mandate | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
Verification, retrieval, evidence access, provider choice and prompt shape still default to "everything": full suites, whole packs, whole chains, strongest model, unstable prompts.

### Success Criteria (Draft)
- [ ] Test selection recall 1.0 on the corpus with fewer tests than the full set.
- [ ] Retrieval top-3 contains the expected passage for every corpus query.
- [ ] `evidence://` resolves one hop and never returns the whole case.
- [ ] Prefix hash identical across tasks for the same capability.

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

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_EXTRAS.md`
