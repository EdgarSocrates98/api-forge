# DEFINE: API Forge Economy Architecture Hardening

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_ARCH_HARDENING |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | [BRAINSTORM](./BRAINSTORM_API_FORGE_ECONOMY_ARCH_HARDENING.md) · `prompt_evo_new_economy_arch.md` |
| **Branch** | `codex/new-economy-arch` |

---

## Problem Statement

The economy architecture claims hard budgets, observed tokens, verified proofs
and safe context, but the code lets out-of-root files be read into `ctx://`,
lets per-instance context shares exceed the envelope, leaves shadow calls
uncounted across resume, reports partial token totals as observed and stops
early on substring matches — so the claims are intentions, not invariants.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Release guardian | Certifies ship | Cannot certify budgets and metrics that the code does not enforce |
| Security reviewer | Owns the threat model | Context Gateway and `evidence resolve` can read files outside the project |
| Agent hosts (Claude, Codex, Devin, Copilot) | Run governed tasks | Shadow and resume can overspend silently; stale knowledge served until restart |
| Maintainer | Reads economy reports | Partial measurements look complete; `protected_overrun` looks `ok` |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | H1: one canonical allowed-root source resolver; gateway and evidence load cases only via `case.service.load_case()` |
| **MUST** | H2: global context budget (class pools), `RoleContextPlan.total_bytes ≤ context_bytes` invariant |
| **MUST** | H2: shadow calls counted by `ControlPlane`; usage breakdown with `total ≤ provider_calls`; checkpoint reflects real calls |
| **MUST** | H2: token coverage `complete\|partial\|unresolved`; ledger persist failure surfaces as `unresolved` |
| **MUST** | H3: L0 only on structured, re-hashed proofs |
| **SHOULD** | H3: stale/corrupt local cache falls through to shared; invalid timestamps = corrupt miss; knowledge LRU keyed by generation |
| **SHOULD** | H4: `PhaseBudgetPlan` `quality_status` + `budget_status`; routing unresolved in run summary; unmapped source degrades delta |
| **SHOULD** | H4: `ShadowDecision.mode` `paired_ab` \| `capability_eval` |
| **SHOULD** | H4: `EconomyMatrix.claim_scope`; agentic-quality eval layer over recorded specialist outputs; evidence classes separated in docs |
| **COULD** | H4: Unicode (NFKC + casefold) retrieval tokenizer; CI runs for merges into `main` |

---

## Success Criteria

- [ ] 8/8 adversarial path/case cases match the review table (refuse `../`, absolute, UNC/drive, symlink-out, undeclared repo; allow nested and declared repo; hash mismatch on edited `facts.json`)
- [ ] Zero case loaders outside `case/service.py` (grep-verifiable)
- [ ] `RoleContextPlan` with `total_bytes > context_bytes` cannot be constructed; 32 KB / 2 specialists / 1 reviewer plan totals ≤ 32 KB
- [ ] After a sampled shadow, `ControlPlane.calls_used` and `economy_checkpoint.json` equal real adapter invocations
- [ ] 1 measured + 2 unmeasured rows → `token_coverage.status = partial`, `observed_rows=1`, `eligible_rows=3`
- [ ] Substring-only proofs never yield L0; structured proof with bad sha256 never yields L0
- [ ] Local stale + shared fresh → hit from shared; invalid timestamp → corrupt miss, no exception
- [ ] Pack edited on disk is returned by `knowledge select/search` in the same process
- [ ] Protected-only overrun → `budget_status=protected_overrun`, `quality_status=ok`
- [ ] Run summary contains routing unresolved; unmapped `src/**/*.py` → delta `degraded`, unmapped `docs/**` informational
- [ ] `autenticação`, `migração`, `configuração` retrieved by PT-BR queries
- [ ] All 7 existing economy evals still pass; new `evals economy-hardening` and `evals agentic-quality` pass

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Traversal | fact `path: ../secret` | `evidence resolve` / capsule | ref `unresolved` `AF-PATH-OUTSIDE-ROOT`; file never read; rest served |
| AT-002 | Absolute/UNC | fact path `/etc/passwd`, `C:\...`, `\\host\share` | resolve | refused per ref |
| AT-003 | Symlink escape | project symlink → outside dir | resolve | refused |
| AT-004 | Workspace roots | declared repo vs undeclared repo | resolve | allow vs refuse |
| AT-005 | Case tamper | `facts.json` edited after `case.json` | capsule | `AF-CASE-HASH-MISMATCH` refusal |
| AT-006 | Context pool | 32 KB envelope, 2 specialists + reviewer | plan roles | total ≤ 32 KB; invalid plan raises |
| AT-007 | Shadow accounting | shadow sampled | run then checkpoint | `calls_used` includes shadow; `usage.shadow_calls=1` |
| AT-008 | Partial tokens | 1 of 3 rows observed | `economy stats` | coverage `partial` |
| AT-009 | Ledger failure | ledger path unwritable | append + stats | `unresolved` persist failure |
| AT-010 | L0 structured | substring-only / bad hash / valid | `deterministic_proof` | L1 / L1 / L0 |
| AT-011 | Cache fall-through | local stale, shared fresh | lookup | shared hit |
| AT-012 | Bad timestamp | entry `created_at: "garbage"` | lookup | corrupt miss |
| AT-013 | Knowledge generation | pack edited in-process | select/search | new content |
| AT-014 | Phase status | only verify overruns | phase-budget | `budget_status=protected_overrun` |
| AT-015 | Routing unresolved | no scorecard observations | runtime run | summary lists routing unresolved |
| AT-016 | Delta unmapped | changed `src/x.py` unmapped | `context delta` | `degraded` |
| AT-017 | Shadow mode | `capability_eval` | shadow | challenger own context; mode recorded |
| AT-018 | PT-BR retrieval | query "autenticação" | `knowledge search` | pack with the term ranked |
| AT-019 | Claim scope | matrix report | `evals economy-matrix` | `claim_scope="deterministic-safety-economy"` |
| AT-020 | Agentic quality | recorded specialist outputs vs ground truth | `evals agentic-quality` | per-case verdict match reported; gate passes |

---

## Out of Scope

- New economy features beyond the review.
- Live model/provider calls inside the core (agentic quality uses recorded or user-supplied outputs).
- A unified BudgetLedger service replacing `ControlPlane`.
- Heuristic automatic choice of shadow mode.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Security | No provider SDK in `src/`; no live mutation; argv-only git | Resolver and evals stay local |
| Compatibility | Contract changes additive (`VersionedContract`, `extra=forbid`) | New fields default-safe; docs updated |
| Governance | Every refusal `AF-*` + `field` + `unlock`, cataloged | Catalog + release gate parity |
| Docs | Bilingual pairs updated together; threat model EN + PT-BR | Doc diff per wave |
| Process | Commit per wave H1–H4; full suite + push at the end | Targeted tests per wave |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/{security,case,context,evidence,runtime,economy,cache,knowledge,evals}`, `.github/workflows/ci.yml` | New `security/source_paths.py` |
| **KB Domains** | repo threat model, catalog contract, contract docs; agentspec python/testing | |
| **IaC Impact** | Modify CI workflow only | Main pushes by `GITHUB_TOKEN` auto-merge do not trigger workflows |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | `case.service.load_case()` exposes everything the gateway reads (api-ir, facts, findings, graph) | Gateway needs a thin adapter over verified artifacts | [ ] |
| A-002 | `WorkspaceManifest` lists target repo roots resolvable locally | Resolver accepts project root only when no manifest | [ ] |
| A-003 | Main squash commits are pushed with `GITHUB_TOKEN`, which does not trigger `push` workflows | CI fix differs (e.g. `workflow_run` or post-merge job) | [x] last `push` CI run on `main` predates PRs #10–#13 |
| A-004 | Adding pools keeps role-context eval ratios within existing gates | Eval gates re-tuned with justification | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Each defect verified in code with file:line |
| Users | 3 | Four personas with pains |
| Goals | 3 | MoSCoW mapped to waves |
| Success | 3 | Numeric/grep-checkable |
| Scope | 2 | Agentic-quality eval shape and CI fix mechanism decided in Design |
| **Total** | **14/15** | |

---

## Open Questions

- Design: exact CI mechanism for merged commits (token swap vs `workflow_run`/post-merge job).
- Design: recorded specialist output format for `evals agentic-quality`.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial from BRAINSTORM |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_ARCH_HARDENING.md`
