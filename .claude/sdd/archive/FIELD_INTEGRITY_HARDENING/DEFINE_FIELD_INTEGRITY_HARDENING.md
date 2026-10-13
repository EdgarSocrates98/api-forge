# DEFINE: Field Integrity Hardening

> Make the field validation harness fail closed on mutated pre-registration, re-labelled annotations, self-verification and premature decisions, before the first real field cycle starts.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | FIELD_INTEGRITY_HARDENING |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 15/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_FIELD_INTEGRITY_HARDENING.md` (from external review `prompt_evo_ajuste.md` of `main@9ca39f9`) |

---

## Problem Statement

The field validation harness (`apiforge field record/annotate/verify/report/export`) can emit a verified, decision-grade result (H1 verdict + "open follow-up SDD") from an edited corpus/hypothesis, an annotation changed after verification, a verifier identical to the executor, or a cycle whose scenario coverage and timebox are incomplete — so the evidence chain that is supposed to decide the next roadmap item is not trustworthy. The cycle has not started (`cycle_started_at: null`, `tasks: []`), so fixing it now costs no data migration.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Owner / field operator | Runs `field record` on real tasks and decides roadmap from `field report` | Cannot prove corpus, hypothesis and gate were fixed before results appeared; `registered_at` is editable YAML |
| Verifier (human or `api-verifier` agent) | Issues blind `agree/disagree/unresolved` verdict | Verdict silently survives later annotation changes (`annotate.py:35` merge) and nothing proves verifier ≠ executor |
| Roadmap consumer (SDD follow-ups) | Acts on `FieldReport.recommendation` | Report may recommend a new SDD after 5 runs of one scenario (`report.py:103-118`); `max_runs`/`max_weeks` never enforced |
| Consumer of `workspace graph --infer` | Uses inferred HTTP relations for impact/security analysis | HTTP relations cite only caller ref; callee route ref dropped (`match.py:129`) |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | G1 — Seal the cycle: `FieldCycleIdentity/v1` written to `docs/field/cycle.lock.json` on first `field record`; every field command recomputes and refuses on mismatch or missing lock |
| **MUST** | G2 — `VerificationReceipt/v1` bound to an annotation digest; any annotation change after verify makes the run `stale` and excludes it from verified counts |
| **MUST** | G3 — Executor/verifier identity (`{kind: human\|agent, id}`); verify refused when verifier id == executor id |
| **MUST** | G4 — Readiness gate: `cycle_status ∈ {collecting, ready, expired}`; H1 decision + SDD recommendation only when `ready`; `max_runs`/`max_weeks` enforced; `record` refused after `expired` |
| **MUST** | G5 — New refusals cataloged (`AF-FIELD-CYCLE-MUTATED`, `AF-FIELD-VERIFIER-NOT-INDEPENDENT`, `AF-FIELD-CYCLE-EXPIRED`) with `code/field/unlock` preserved in CLI and MCP |
| **MUST** | G6 — Corpus gate raised to `max_runs: 40` (slack for disagree/stale) before the cycle is sealed |
| **SHOULD** | G7 — HTTP inferred relations carry caller ref and callee route ref (parity with topic inference) |
| **SHOULD** | G8 — `field export` carries `cycle_status` and lock hashes; `docs/field/README.md` documents lock, receipt, statuses, refusals |
| **COULD** | G9 — Lock records optional `git_commit` when `git` is available (never blocks) |

---

## Success Criteria

- [ ] 100% of 7 tamper scenarios fail closed with the expected AF code (edited hypothesis, edited corpus task, backdated `registered_at`, edited gate, deleted lock, self-verification, record after expiry).
- [ ] annotate-after-verify: run appears in `stale_runs` and `unresolved_runs`; 0 stale runs counted in `runs_verified`.
- [ ] Early stop scenario (5 verified `graph_gap` runs, 1 scenario, 2 repos) yields `cycle_status=collecting`, `h1_verdict=inconclusive`, `provisional_h1=confirmed`, recommendation containing "continue collecting" and not "open follow-up".
- [ ] Full coverage scenario (≥5 verified runs in each of 6 scenarios, within timebox) yields `cycle_status=ready` and a non-provisional `h1_verdict`.
- [ ] Timebox scenarios: `runs_total ≥ 40` without coverage, and elapsed > 4 weeks without coverage, each yield `expired` + `inconclusive` + "extend corpus; open no new feature".
- [ ] HTTP inference fixture: 100% of inferred `calls` relations contain both caller and callee route refs.
- [ ] Existing `tests/field/*` and workspace inference suites stay green (baseline: 170 passed / 1 skipped focused suite); `apiforge sdd check --root docs/sdd` passes; `apiforge agents lint` unaffected.
- [ ] 3 new AF codes present in `docs/catalog-contract.md` and surfaced with `code/field/unlock` by both CLI and MCP field tools.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Seal on first record | corpus with tasks, `cycle_started_at: null`, no lock | `field record` for a registered task | `cycle_started_at` set; `cycle.lock.json` written with corpus/hypothesis/gate/task-ids/repo-set sha256; `corpus_sha256` stable after `cycle_started_at` write |
| AT-002 | Hypothesis tampered | sealed cycle | `hypothesis.md` edited, then any field command | `AF-FIELD-CYCLE-MUTATED`, field=`cycle`, unlock names restore/new cycle |
| AT-003 | Corpus backdated | sealed cycle | task added with `registered_at` before `cycle_started_at` | `AF-FIELD-CYCLE-MUTATED` (task-id set hash differs) |
| AT-004 | Lock deleted | `cycle_started_at` set | `cycle.lock.json` removed, then `field report` | `AF-FIELD-CYCLE-MUTATED` |
| AT-005 | CRLF checkout | sealed cycle | `hypothesis.md` re-checked-out with CRLF, content same | no mutation detected (LF-normalized hash) |
| AT-006 | Stale verification | run annotated `graph_gap`, verified `agree` | `annotate --exit-reason context_gap` | report lists run in `stale_runs` + `unresolved_runs`; not counted in any theme |
| AT-007 | Re-verify clears stale | AT-006 state | `verify` again by independent verifier | new receipt matches current digest; run counted under `context_gap` |
| AT-008 | Self verification | run recorded with executor `agent:api-orchestrator` | `verify --verifier agent:api-orchestrator` | `AF-FIELD-VERIFIER-NOT-INDEPENDENT`; run unchanged |
| AT-009 | Human anonymized id | — | `verify --verifier human:<raw-name>` | refused unless id is `sha256:<hex>` (`AF-FIELD-ENUM` or dedicated field error per Design) |
| AT-010 | Early stop | 5 verified `multi_repo` `graph_gap` runs over 2 repos | `field report` | `collecting`, `h1_verdict=inconclusive`, `provisional_h1=confirmed`, recommendation "continue collecting" |
| AT-011 | Ready | ≥5 verified runs per each of 6 scenarios, within 40 runs / 4 weeks | `field report` | `ready`; `h1_verdict` ∈ {confirmed, refuted} per existing rule; SDD recommendation allowed (≤2 themes) |
| AT-012 | Expired by runs | 40 baseline runs, a scenario < 5 verified | `field report` | `expired`, `inconclusive`, "extend corpus; open no new feature" |
| AT-013 | Expired by weeks | `cycle_started_at` > 4 weeks ago, coverage incomplete | `field report` | `expired` (clock injectable for test) |
| AT-014 | Record after expiry | expired cycle | `field record` | `AF-FIELD-CYCLE-EXPIRED` |
| AT-015 | HTTP provenance | repo A outbound `GET /orders/{id}`, repo B serves it | `workspace graph --infer` | `calls` relation refs ⊇ {A caller ref, B route ref} |
| AT-016 | Export | sealed ready cycle | `field export` | export contains `cycle_status` and lock hashes; no leak check regression |
| AT-017 | MCP parity | any refusal above | same op via MCP field tool | same `code`, `field`, `unlock` as CLI |

---

## Out of Scope

- New inference protocols (gRPC, GraphQL, AsyncAPI, Arazzo, runtime telemetry).
- Append-only event ledger / replay model for field runs.
- Key-based signing of the lock; mandatory `git_commit`.
- Multiple verification receipts per run (history); single receipt, re-verify replaces.
- `field reset` / new-cycle command (new cycle = manual new corpus).
- Pinning OTel Demo commit and populating corpus tasks (owner action after ship).
- Changes to agent roster or host mirrors (`.codex/agents`, `.claude/agents`).
- Migration of existing run files (none exist).

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | No provider SDK imports in `src/`; local-first; no live mutation | Pure stdlib hashing (`hashlib`, canonical `json.dumps(sort_keys=True, separators=(",",":"))`) |
| Technical | New contracts registered in `src/apiforge/contracts/registry.py` (`FieldCycleIdentity/v1`, `VerificationReceipt/v1`) | Registry + contract tests updated |
| Technical | Every refusal keeps `AF-*` code, `field`, `unlock` in CLI/MCP and is cataloged in `docs/catalog-contract.md` | Catalog + surface tests |
| Technical | `mark_cycle_started` rewrites `corpus.yaml`; corpus hash must exclude `cycle_started_at` | Canonical hash over parsed mapping minus that key |
| Technical | Windows + Linux checkouts | Hypothesis hash LF-normalized |
| Technical | `max_runs: 40` change is legal only before sealing | Change lands in this feature, before any record |
| Process | Edits via `apply_patch`; tests + SDD artifacts updated together; `apiforge sdd check --root docs/sdd` before ship | — |
| Process | Targeted tests per task, full suite once before ship; pytest basetemp outside repo (`E:/afpt`) | — |
| Timeline | Must land before first real field record | Blocks field cycle start |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/field/{corpus,record,annotate,report,export,store,errors}.py`, new `src/apiforge/field/identity.py` (Design decides), `src/apiforge/contracts/field.py`, `src/apiforge/contracts/registry.py`, `src/apiforge/workspace/inference/match.py`, CLI field commands, `src/apiforge/mcp/tools.py`, `docs/catalog-contract.md`, `docs/field/{README.md,corpus.yaml}`, `tests/field/*`, inference tests | Contained to field + inference modules |
| **KB Domains** | agentspec: `pydantic`, `testing`, `python`. Project skills: `api-forge-sdd`, `api-forge-verification`. Codebase pattern: `BenchmarkIdentity/v1` (`contracts/economy_evals.py:46`, `same_experiment()`) | Mirror identity pattern |
| **IaC Impact** | None | Local-first CLI |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | No field run files exist yet (cycle unstarted) | Would need migration of `verifier_verdict` → receipt | [x] `corpus.yaml` `tasks: []`, `cycle_started_at: null` |
| A-002 | Contract change to `FieldRun` (replace/derive `verifier_verdict`) breaks no external consumer | Would need backward-compatible alias field | [ ] Design checks MCP/export consumers |
| A-003 | Lockfile committed alongside corpus is acceptable repo hygiene | Would need lock outside repo → loses Git proof | [x] Approach A confirmed in brainstorm |
| A-004 | Scenario coverage is the right readiness signal; theme/repo minimums stay in qualification | Readiness might need repo-count too | [ ] Revisit after first cycle |
| A-005 | Clock can be injected in report/record for deterministic timebox tests | Tests would be time-flaky | [ ] Design confirms seam |
| A-006 | 40 runs gives enough slack (~33%) for disagree/stale/unresolved | Cycle may still expire; conclusion "extend corpus" is still honest | [ ] Observed during cycle |
| A-007 | Callee `Served.ref` already carries `repo:file:line` | HTTP provenance would need extractor change | [x] `match.py:26-40` dataclasses carry `ref` |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Each hole verified with file:line evidence |
| Users | 3 | Four personas with concrete pain tied to code |
| Goals | 3 | MoSCoW, each maps to invariant + AT |
| Success | 3 | Numeric/boolean criteria, 17 ATs |
| Scope | 3 | Explicit out-of-scope from YAGNI + owner follow-ups |
| **Total** | **15/15** | |

---

## Open Questions

None blocking. Delegated to Design:
- Whether `verifier_verdict` stays as a derived read-only property or is removed (A-002).
- Error code for non-anonymized human id (reuse `AF-FIELD-ENUM` vs dedicated).
- Clock injection seam for timebox (A-005).
- Whether `FieldGate.max_runs` contract default moves from 30 to 40 or only `corpus.yaml` changes.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial version from BRAINSTORM; `max_runs` raised to 40 per owner decision |
| 1.1 | 2026-09-28 | ship-agent | Shipped and archived |

---

## Next Step

**Next Step:** `/build .claude/sdd/features/DESIGN_FIELD_INTEGRITY_HARDENING.md` (use `/agentspec:workflow:build` to avoid the SPEC.md skill collision)
