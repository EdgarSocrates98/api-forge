# BRAINSTORM: API Forge Economy Architecture Hardening

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_ARCH_HARDENING |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |
| **Source** | `prompt_evo_new_economy_arch.md` (external review of `main`, verdict `REVIEW`) |
| **Branch** | `codex/new-economy-arch` |

---

## Initial Idea

**Raw Input:** An external review of the completed economy program (waves 0–8)
says the architecture is right but not yet `PASS`: four P1 problems break
security or the truthfulness of budgets and metrics, plus P2/P3 gaps. No new
economy features until "hard budget", "observed", "verified" and "safe" are
code invariants, not intentions.

**Context Gathered (verified in code on this branch):**
- P1 case/path: `context/gateway/levels.py:83` has its own `load_case` that bypasses `case/service.load_case()` (manifest, containment, re-hash, `AF-CASE-HASH-MISMATCH`); `evidence/resolve.py:81` joins `props.path` to the project root with no containment check.
- P1 context budget: `runtime/role_context.py:124` applies `share × context_bytes` per role instance, so N specialists can exceed the envelope; `RoleContextPlan` has no `total_bytes ≤ context_bytes` invariant.
- P1 shadow: `_shadow` (`runtime/supervisor.py:509`) calls `adapter.invoke` without `control.start`, so `calls_used` and `economy_checkpoint.json` undercount.
- P1 tokens: `economy/run_ledger.py:74–94` uses `tokens_seen` (any row measured) and reports a partial total as fully observed.
- P2: `deterministic_proof()` (`runtime/economy.py:247`) matches free-text `expected_proofs` by substring in serialized steps.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/{security,case,context,evidence,runtime,economy,cache,knowledge,evals}` | New `security/source_paths.py`; changes are mostly additive fields and validators |
| Relevant KB Domains | repo: `docs/security/threat-model-mvp*.md`, `docs/catalog-contract.md`, `docs/contracts/*`; agentspec KB: python, testing | Threat model rows, AF catalog, contract docs must move with code |
| IaC Patterns | N/A (CI only: `.github/workflows`) | CI trigger on `main` push is in scope |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Scope: P1 only, P1+P2, or all in waves? | All (P1+P2+P3) in waves H1–H4, commit per wave | Four waves; full suite + push only at the end |
| 2 | Path outside allowed roots: refuse ref or whole command? | Refuse the ref, serve the rest; case hash mismatch still refuses everything | `AF-PATH-OUTSIDE-ROOT` as `unresolved` per ref; tampered case = hard refusal |
| 3 | Shadow challenger context semantics? | Declared mode, default `paired_ab`; `capability_eval` builds the challenger's own context | `ShadowDecision.mode`; shadow counted by `ControlPlane` |
| 4 | How to harden L0 proof? | Structured proofs + verifier (id/kind/sha256/artifact_ref, re-hash) | Free-text proofs never reach L0 (at most L1 + `AF-ECONOMY-PROOF-UNSTRUCTURED`) |
| 5 | Samples / ground truth? | Prompt's P1 table + existing fixtures and corpora | Adversarial path corpus + regression on 7 existing evals |
| 6 | What to defer (YAGNI)? | Nothing — include everything | Agentic-quality eval layer, CI trigger fix and auditable ledger mode are in scope |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/economy_payments/`, `evals/corpus/economy*/` | 7 corpora | Regression for gateway, routing, cache, selective, tool, extras, freshness |
| Output examples | `docs/contracts/*-v1.md` | ~40 economy contracts | Shapes to extend additively |
| Ground truth | Prompt P1 table (8 path/case cases); prompt budget example (32 KB, 2 specialists → 38.4 KB) | 8 + scenarios | Becomes `evals/corpus/economy-hardening/` |
| Related code | `case/service.py::load_case`, `runtime/control.py::ControlPlane`, `cache/store.py` | — | Canonical primitives to reuse |

**How samples will be used:** path/case table → adversarial tests (must refuse /
must allow); budget example → invariant test; existing corpora → no regression.

---

## Approaches Explored

### Approach A: Invariants in contracts + single primitives ⭐ Recommended

**What:** One canonical `resolve_allowed_source`; gateway and evidence load the
case only through `case.service.load_case()`; budget/accounting rules become
`model_validator` invariants on contracts; `ControlPlane` is the single call
counter; token coverage is explicit; L0 needs structured, re-hashed proofs.

**Pros:**
- Guarantees live in code; invalid states cannot be constructed.
- Removes the duplicated case loader.
- Matches repo precedent (`BudgetEnvelope.silent_downgrade: Literal[False]`, validators on `ScorecardCandidateAssessment`).

**Cons:**
- Touches published contracts (mitigated: additive/optional fields only).

**Why Recommended:** The review explicitly asks for invariants, not intentions; codebase precedent (confidence 0.95).

---

### Approach B: Guard layer at the edges

**What:** Post-filter capsule/evidence output and add checks at emission points; keep internals.

**Pros:** small diff.
**Cons:** duplicated loader stays; contracts still accept invalid states; next route reopens the bug.
**Why not:** treats symptoms.

---

### Approach C: Rewrite gateway on the case service + unified BudgetLedger

**What:** New budget service unifying calls/bytes/tokens; gateway rebuilt.
**Pros:** cleanest architecture.
**Cons:** large diff, high regression risk across 7 evals; review asks for hardening, not features.
**Why not:** scope and risk.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28, explicit choice in session |
| **Reasoning** | Invariants in contracts with single canonical primitives |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Allowed roots = project root + repos declared in `WorkspaceManifest` | multi-repo workspaces are first-class; undeclared repos are foreign | project root only |
| 2 | Out-of-root ref → `unresolved` `AF-PATH-OUTSIDE-ROOT`, rest served; case hash mismatch → full refusal | one poisoned fact must not DoS analysis; tampered case must | refuse whole command |
| 3 | Context budget = global envelope → class pools → instances; validator `total_bytes ≤ context_bytes` | "hard budget" must hold with N agents | per-instance share |
| 4 | Shadow counted by `ControlPlane`; usage breakdown `primary/review/shadow/total`, `total ≤ provider_calls` | single source of truth survives resume | parallel counters |
| 5 | `ShadowDecision.mode`: `paired_ab` (default) \| `capability_eval` | makes comparison semantics explicit | implicit primary context |
| 6 | `TokenCoverage{status, observed_rows, eligible_rows}`; total "observed" only when complete | never claim unmeasured tokens | boolean `tokens_seen` |
| 7 | L0 requires structured proofs (id, kind, sha256, artifact_ref) verified by re-hash | early stop must rest on receipts | substring match |
| 8 | Stale/corrupt local cache falls through to shared; invalid timestamps = corrupt miss | no wasted recompute, no exceptions | miss on local stale |
| 9 | Knowledge LRU keyed by knowledge generation (pack.yaml hash + mtimes) | long-lived MCP sees refreshed packs | restart required |
| 10 | `PhaseBudgetPlan.quality_status` + `budget_status` | protected overrun is not "ok" nor failure | single status |
| 11 | Agentic quality as a separate eval layer over recorded/provided specialist outputs; matrix claim scoped | honest claims; core stays provider-free | model calls in core |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Live model calls for agentic-quality eval | Core must stay provider-free; eval consumes recorded responses or user-provided transcripts instead | Yes (host-side runner) |
| New unified BudgetLedger service (Approach C) | Hardening, not re-architecture; `ControlPlane` already is the counter | Yes |
| Automatic shadow context selection per capability | Mode is declared explicitly; no heuristic chooser | Yes |

User explicitly chose to keep every review item in scope (P1+P2+P3, CI trigger, auditable ledger, agentic-quality layer); removals above only trim *how* items are built.

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| H1 trust boundary + H2 budget/accounting | ✅ | Approved | No |
| H3 proof/cache + H4 reporting/evals/CI | ✅ | Approved | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
The economy architecture claims hard budgets, observed tokens, verified proofs
and safe context, but the code allows out-of-root file reads into `ctx://`,
per-instance context shares that exceed the envelope, uncounted shadow calls,
partial token totals reported as complete, and substring-based early stops.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Release guardian | Cannot certify budgets/metrics that are not invariants |
| Security reviewer | Gateway/evidence can read files outside the project |
| Agent hosts (Claude/Codex/Devin/Copilot) | Resume and shadow can overspend silently |

### Success Criteria (Draft)
- [ ] 8/8 adversarial path/case cases behave as the review table (refuse/allow/hash mismatch)
- [ ] No code path loads a case except `case.service.load_case()`
- [ ] Constructing `RoleContextPlan` with `total_bytes > context_bytes` raises; 32 KB / 2 specialists stays ≤ 32 KB
- [ ] Shadow call increments `calls_used`; checkpoint after shadow equals real calls
- [ ] Partial token rows → `coverage: partial`, never `tokens_unresolved: false` with a complete claim
- [ ] L0 only with structured, re-hashed proofs; substring cases fall to L1
- [ ] Local stale + shared fresh → hit; invalid timestamp → corrupt miss
- [ ] Knowledge change on disk visible without restart
- [ ] Protected overrun → `budget_status: protected_overrun`, never plain `ok`
- [ ] Routing unresolved visible in run summary; unmapped source file degrades delta
- [ ] PT-BR terms retrieved (autenticação, migração, configuração)
- [ ] Ledger persist failure → `unresolved`
- [ ] Matrix `claim_scope` set; agentic-quality eval layer passes on recorded corpus
- [ ] CI runs on `main` pushes (check-runs present)
- [ ] All 7 existing economy evals still pass

### Constraints Identified
- Offline, deterministic, no provider SDK in `src/`; additive contract changes only.
- Every refusal: `AF-*` + `field` + `unlock`, cataloged; threat model (EN + PT-BR) updated.
- Bilingual docs updated in pairs.

### Out of Scope (Confirmed)
- New economy features beyond the review.
- Live model execution inside the core.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 6 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 3 (implementation trims) |
| Validations Completed | 2 |
| Duration | 1 session |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_ARCH_HARDENING.md`
