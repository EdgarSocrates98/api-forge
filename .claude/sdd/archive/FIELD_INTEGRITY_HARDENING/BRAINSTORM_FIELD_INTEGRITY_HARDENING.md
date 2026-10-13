# BRAINSTORM: Field Integrity Hardening

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | FIELD_INTEGRITY_HARDENING |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |

---

## Initial Idea

**Raw Input:** `prompt_evo_ajuste.md` — external review of `main@9ca39f9` (field validation harness + opt-in cross-repo inference, PR #20/#21). Verdict: direction approved; do a small **Field Integrity Hardening** before the first real field collection, then stop building and use the tool.

**Context Gathered:**
- Field cycle not started: `docs/field/corpus.yaml` has `cycle_started_at: null`, `tasks: []` → no persisted run data to migrate.
- Every review claim verified against code (branch `sdd/agent-roster`, field code from `010d3d6`):
  - `src/apiforge/field/annotate.py:35` `_update()` blindly merges changes; `annotate` after `verify` keeps `verifier_verdict=agree` over a changed `exit_reason`.
  - `src/apiforge/field/corpus.py:61` only checks `hypothesis.md` exists; no hash of hypothesis/corpus; `registered_at` is editable YAML.
  - `src/apiforge/field/report.py:103-118` computes `h1_verdict` and "open follow-up SDDs" recommendation even when `scenarios_under_min` is non-empty.
  - `src/apiforge/workspace/inference/match.py:129` HTTP relation refs keep only `call.ref`; `Served.ref` (callee route) dropped. `_topics` already keeps producer + consumer refs.
  - `FieldRun` has only `verifier_verdict`; no executor/verifier identity.
- **Extra finding (not in review):** `FieldGate.max_runs` / `max_weeks` (`src/apiforge/contracts/field.py:50-51`) are declared but never enforced anywhere.
- Precedent: `BenchmarkIdentity/v1` + `same_experiment()` in `src/apiforge/contracts/economy_evals.py:46`, registered in `contracts/registry.py`.
- Scenarios: 6 (`maintenance, evolution, security, multi_repo, incident, performance`) × `min_tasks_per_scenario=5` = 30 = `max_runs` → zero slack.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/field/*`, `src/apiforge/contracts/field.py`, `src/apiforge/contracts/registry.py`, `src/apiforge/workspace/inference/match.py`, CLI/MCP field surfaces, AF code catalog, `docs/field/README.md`, `tests/field/*` | Small, contained diff |
| Relevant KB Domains | agentspec KB: `pydantic`, `testing`, `python` (generic only; KB is data-eng oriented). Project skills: `api-forge-sdd`, `api-forge-verification`, `api-forge-context` | Codebase pattern (`BenchmarkIdentity/v1`) outweighs KB |
| IaC Patterns | N/A | Local-first; no infra |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Which review items enter scope? | All 4 (cycle identity, verification receipt + verifier id, readiness gate, HTTP route ref) **plus** timebox enforcement (`max_runs`/`max_weeks`) | Hardening covers every integrity hole before first run |
| 2 | What happens when `annotate` runs after `verify`? | Digest + stale: receipt stores `annotation_sha256`; mismatch → run `stale` → `unresolved` | History preserved, auditable; no silent re-labelling |
| 3 | Executor ≠ verifier enforcement? | Record `executor {kind,id}`; `verify` requires `verifier {kind: human\|agent, id}`; same id → refuse `AF-FIELD-VERIFIER-NOT-INDEPENDENT`; humans use `sha256:` anonymized id | Blind-verifier becomes checkable, not only procedural |
| 4 | When is the cycle `ready` for H1 + roadmap recommendation? | Coverage **or** timebox end: `ready` = all scenarios ≥ min; timebox exceeded without coverage → `expired` (H1 inconclusive, "extend corpus"); otherwise `collecting` → "continue collecting" | Prevents early stopping on a convenient result |
| 5 | Samples / ground truth? | Existing fixtures (`tests/field/support.py`, inference fixtures) extended with tamper cases; no real data yet | Synthetic but adversarial test corpus |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `docs/field/corpus.yaml`, `docs/field/hypothesis.md` | 2 | Real pre-registration artifacts; corpus empty |
| Output examples | `FieldReport` via `tests/field/test_annotate_report.py` | 1 suite | Current report shape to extend |
| Ground truth | `docs/field/ground-truth/` | dir | Unused until cycle starts |
| Related code | `tests/field/support.py`, `test_record.py`, `test_annotate_report.py`, `test_export_parity.py`; `contracts/economy_evals.py` (`BenchmarkIdentity`) | 5 | Fixtures + identity pattern to mirror |

**How samples will be used:**

- Extend `tests/field/support.py` fixtures with tamper scenarios: hypothesis edited post-start, corpus/task backdated, lock deleted, annotate after verify, self-verification, early stop (5 × `multi_repo` only), timebox expired, record after expiry.
- HTTP inference fixture asserting both caller and callee route refs.
- `BenchmarkIdentity/v1` as schema/method reference for `FieldCycleIdentity/v1`.

---

## Approaches Explored

### Approach A: Sealed lockfile + embedded receipt ⭐ Recommended

**Description:** First `field record` writes `docs/field/cycle.lock.json` (`FieldCycleIdentity/v1`). Every field command recomputes and compares. `FieldRun` gains `executor` and `verification: VerificationReceipt/v1`. `summarize` derives `stale`, `cycle_status`, `coverage_gate`, `provisional_h1`.

**Pros:**
- Mirrors in-repo `BenchmarkIdentity/v1` / `same_experiment()` (confidence 0.80, codebase pattern).
- Minimal, contained diff in `field/*` + contracts.
- Committed lockfile ties external Git proof to runtime checks.

**Cons:**
- Lockfile deletable → mitigated: `cycle_started_at` set ∧ lock missing ⇒ `AF-FIELD-CYCLE-MUTATED`.

**Why Recommended:** Smallest change that turns pre-registration into an invariant; reuses an established repo pattern.

---

### Approach B: Inline hashes in `corpus.yaml`

**Description:** `mark_cycle_started` writes an `identity:` block inside the corpus.

**Pros:**
- One file fewer.

**Cons:**
- Self-referential hash needs canonicalization excluding the block.
- `mark_cycle_started` already rewrites YAML (loses comments) → more fragile; mixes declaration with seal.

---

### Approach C: Append-only event ledger

**Description:** Every `record/annotate/verify` becomes an event (reuse `economy/run_ledger.append`); report replays.

**Pros:**
- Full history, strongest tamper evidence.

**Cons:**
- Rewrites field storage model; far beyond the "small hardening" the review asks for; YAGNI before first collection.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28 (brainstorm session) |
| **Reasoning** | Mirrors existing `BenchmarkIdentity/v1`; minimal diff; lockfile + Git commit make pre-registration tamper-evident |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | `FieldCycleIdentity/v1` in `docs/field/cycle.lock.json`, written on first `record` | Invariant instead of convention; committed with corpus | Inline hashes (B), event ledger (C) |
| 2 | `corpus_sha256` over canonical corpus **excluding** `cycle_started_at` | `mark_cycle_started` writes that field; must not self-invalidate | Raw-bytes hash |
| 3 | `hypothesis_sha256` over LF-normalized bytes | Windows/Linux checkout parity | Raw bytes |
| 4 | `VerificationReceipt/v1` embedded in `FieldRun`; single receipt, re-verify replaces | Simple; stale detection via digest | Receipt history list |
| 5 | `annotation_sha256` = canonical hash of annotatable fields (exit_reason, task_completed, manual_context_required, human_intervention, false_positives, false_negatives) | Any annotation change after verify is detectable | Clear verdict on annotate; lock annotate |
| 6 | `executor`/`verifier` = `{kind: human\|agent, id}`; human id `sha256:<hex>`; agent id = roster name (e.g. `api-verifier`) | Proves executor ≠ verifier; privacy for humans | kind-only |
| 7 | `h1_verdict` ∈ {confirmed, refuted} only when `cycle_status == ready`; otherwise `inconclusive`, with `provisional_h1` always exposed | Separate observation from decision eligibility | Report verdict from any subset |
| 8 | `record` after `expired` refused (`AF-FIELD-CYCLE-EXPIRED`) | No extending a cycle until result looks convenient | Timebox informative only |
| 9 | Lock mismatch fails the command (`AF-FIELD-CYCLE-MUTATED`) rather than emitting `invalid` report silently | Tampered cycle must not produce numbers | Report with warning |
| 10 | HTTP inferred relation refs = `{call.ref, route.ref}` | Auditable from both sides; parity with `_topics` | Caller ref only |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Append-only event ledger | Approach C rejected; receipt + lock suffice | Yes |
| Cryptographic signing of lock (keys) | Git commit + hash prove correspondence; no key management | Yes |
| Mandatory `git_commit` in lock | Kept optional (filled when `git` available); must not block | Yes |
| gRPC / GraphQL / AsyncAPI / Arazzo inference | Review: only after field data | Yes |
| Pin OTel Demo commit + fill corpus tasks | Owner operational step after hardening; listed in ship checklist | Yes (next step) |
| Multiple verification receipts per run | Single receipt; old one becomes stale anyway | Yes |
| Changing Codex agent mirrors | Review: acceptable as generated projection | N/A |
| `field reset` / new-cycle command | Mutation = invalid cycle; new cycle is a manual new corpus | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Contracts + invariants V1–V6 (identity, receipt, stale digest, independence, ids, HTTP refs) | ✅ | Approved as presented | No |
| Report / readiness semantics (cycle_status, coverage_gate, provisional_h1, expired refusal, export) | ✅ | Approved as presented | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
The field validation harness can report a verified, decision-grade result from mutated pre-registration, re-labelled annotations, self-verification or an incomplete cycle, so its evidence chain is not trustworthy before the first real collection.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Owner running the field cycle | Cannot prove corpus/hypothesis were fixed before results appeared |
| Verifier (human or `api-verifier`) | Verdict silently survives later annotation changes |
| Roadmap decision (SDD follow-ups) | Report may recommend a new SDD before coverage is reached |
| Consumers of `workspace graph --infer` | HTTP relations not auditable on callee side |

### Invariants (Draft)
- V1: first `field record` → write `cycle.lock.json` (`FieldCycleIdentity/v1`); ∀ `record/annotate/verify/report/export` recompute identity → mismatch → `AF-FIELD-CYCLE-MUTATED` (field=`cycle`).
- V2: `cycle_started_at` set ∧ lock missing → `AF-FIELD-CYCLE-MUTATED`.
- V3: receipt `annotation_sha256` ≠ current → run `stale` → ∈ `unresolved_runs` & `stale_runs`; ∉ verified counts.
- V4: `verify` with `verifier.id == executor.id` → `AF-FIELD-VERIFIER-NOT-INDEPENDENT`.
- V5: human ids `sha256:<hex>`; agent ids = roster agent name.
- V6: HTTP inferred relation refs ⊇ {caller ref, callee route ref}.
- V7: `cycle_status` ∈ {collecting, ready, expired}; `ready` ⇔ ∀ scenario verified ≥ `min_tasks_per_scenario` ∧ within timebox.
- V8: `expired` ⇔ (`runs_total ≥ max_runs` ∨ elapsed > `max_weeks`) ∧ ¬ready → `h1_verdict=inconclusive`, recommendation "extend corpus; open no new feature".
- V9: `collecting` → recommendation = "continue collecting"; ⊥ "open follow-up SDD".
- V10: `record` when `expired` → `AF-FIELD-CYCLE-EXPIRED`.
- V11: every new AF code cataloged; CLI + MCP preserve `code`, `field`, `unlock`.

### Success Criteria (Draft)
- [ ] Tamper tests fail closed: edited hypothesis, edited/backdated corpus task, deleted lock → `AF-FIELD-CYCLE-MUTATED`.
- [ ] annotate-after-verify → run reported `stale` and excluded from verified counts.
- [ ] self-verification → `AF-FIELD-VERIFIER-NOT-INDEPENDENT`.
- [ ] 5 × `multi_repo` graph_gap runs across 2 repos → `cycle_status=collecting`, `h1_verdict=inconclusive`, `provisional_h1=confirmed`, recommendation "continue collecting".
- [ ] timebox exceeded without coverage → `expired`; further `record` refused.
- [ ] HTTP inferred relation carries both refs.
- [ ] Existing field + inference suites stay green; `apiforge sdd check --root docs/sdd` passes; `docs/field/README.md` documents lock, receipt, statuses.

### Constraints Identified
- No provider SDK imports in `src/`; local-first; edits via `apply_patch`.
- New contracts registered in `contracts/registry.py` (`FieldCycleIdentity/v1`, `VerificationReceipt/v1`).
- Every refusal cataloged with `AF-*` code, `field`, `unlock` in CLI and MCP.
- Tests + SDD artifacts updated together; targeted tests per task, full suite once before ship; pytest basetemp outside repo (`E:/afpt`).
- Cycle not started → contract change needs no data migration; `verifier_verdict` may be replaced by the receipt.

### Open Items for Define
- **Zero-slack gate:** 6 scenarios × 5 = 30 = `max_runs`; any `disagree`/stale run forces `expired`. Decide whether to raise `max_runs` (e.g. 40) — only legal before cycle start.
- Whether `report` on a mutated cycle exits non-zero or returns a structured refusal only (align with existing CLI refusal convention).
- Exact canonicalization function (reuse existing canonical JSON helper if present).

### Out of Scope (Confirmed)
- New inference protocols (gRPC, GraphQL, AsyncAPI, Arazzo).
- Event ledger, key-based signing, reset command.
- Pinning OTel Demo / populating corpus tasks (owner action after ship).
- Codex/Claude agent mirror changes.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 discovery + approach + YAGNI |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 8 |
| Validations Completed | 2 |
| Duration | ~1 session |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_FIELD_INTEGRITY_HARDENING.md`
