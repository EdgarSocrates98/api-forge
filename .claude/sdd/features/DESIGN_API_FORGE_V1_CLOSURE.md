# DESIGN: API Forge v1 Closure

> Technical design for implementing API Forge v1 Closure — the 9 residual requirements of `prompt_evo_api_forge_v1.md`

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_V1_CLOSURE |
| **Date** | 2026-09-22 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_V1_CLOSURE.md](./DEFINE_API_FORGE_V1_CLOSURE.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     API_FORGE_V1_CLOSURE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PerformanceRun / facts                                              │
│       │                                                              │
│       ▼                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐    │
│  │ perf/run_    │   │ perf/noise   │   │ perf/suggest         │    │
│  │ store.py     │   │ .py          │   │ .py                  │    │
│  │ append-only  │   │ variance of  │   │ findings ->          │    │
│  │ runs.jsonl   │   │ repeat runs  │   │ ActionPlan (never    │    │
│  │ + search     │   │ -> floor     │   │ applies)             │    │
│  └──────┬───────┘   └──────┬───────┘   └──────────┬───────────┘    │
│       │                  │                      │                  │
│       ▼                  ▼                      ▼                  │
│  .apiforge/perf/   verdict cites floor    ActionPlan JSON          │
│  runs.jsonl        when |delta|<floor     (evidence only)          │
│                                                                      │
│  inventory.facts ──► index/build.py ──► 12 index kinds              │
│                       (derivation,     files symbols routes facts   │
│                        no new parsers) schemas deps calls tests     │
│                                        iac databases findings       │
│                                        decisions                    │
│                                                                      │
│  autonomy/heal.py — structured runbook:                              │
│  detect -> explain -> propose -> authorize -> execute ->            │
│  verify -> compare -> accept|rollback                                │
│  every transition passes policy.decide(); ledger.jsonl records all   │
│                                                                      │
│  knowledge loader: eval `type` in closed 11-value set                │
│  tests/labs/matrix.yaml: technology x case -> fixture/eval           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `perf/run_store.py` | Append-only PerformanceRun memory (`runs.jsonl`), keyed by payload sha256; `search(subject, tool, since)` filters declared fields only | Python, json |
| `perf/noise.py` | `noise_floor(runs)` — variance (max-min)/mean per metric across repeated same-subject runs; returns `None` when <2 runs — floor unproven, never assumed | Python, statistics |
| `perf/suggest.py` | Reads perf findings + facts → emits `ActionPlan` contract (or textual diff block); pure function, writes nothing | Python, contracts |
| `index/build.py` | +8 derived index kinds from existing facts | Python |
| `autonomy/heal.py` | Self-healing pipeline as ordered runbook stages; each stage calls `decide()` and appends to `ledger.jsonl` | Python, policy engine |
| `autonomy/modes.py` | Keep 3 modes; add `V1_MODE_MAP` constant documenting the v1 5-mode reconciliation | Python, StrEnum |
| `knowledge/loader.py` | eval `type` field validated against closed 11-value set | Python, YAML |
| `tests/labs/matrix.yaml` | Declared technology × case → fixture/eval pointer | YAML |

---

## Key Decisions

### Decision 1: Autonomy — keep 3 modes, map v1's 5 onto mode × class

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** v1 asks for 5 modes (`observe/recommend/sandbox/approved/continuous`); the implementation has 3 (`observe/supervised/continuous`). Assumption A-002 in the DEFINE.

**Choice:** Keep the 3 modes; record `V1_MODE_MAP` in `modes.py` and an ADR: v1's `recommend`/`sandbox`/`approved` are class-level behaviors the policy engine already expresses per action class — `read_only`/`local_reversible` auto-execute under `supervised` (that's v1 `sandbox`), `sensitive`/`external_mutation` gate and proceed with approval evidence (that's v1 `approved`), and `observe` evaluates+records decisions without executing (that's v1 `recommend`'s proposal surface, minus a named proposal artifact — which the ledger entry already is). `continuous` matches both specs.

**Rationale:** Modes are the *execution posture* axis; classes are the *permission* axis. v1 conflates them — implementing 5 modes would duplicate policy semantics in mode names and force a vocabulary migration across dispatch, runbooks, docs, and tests for zero behavioral gain.

**Alternatives Rejected:**
1. Migrate to the literal 5 modes — rejected: splits one axis in two, forces mode×class ambiguity (what is `sandbox` + `destructive`?), and migrates vocabulary for cosmetics.
2. Do nothing — rejected: silent divergence from the spec is exactly what this feature exists to close.

**Consequences:**
- Trade-off: the surface vocabulary differs from v1's literal names — mitigated by the ADR + `V1_MODE_MAP` making the correspondence explicit.
- Benefit: no behavioral migration; the ADR is the auditable record.

---

### Decision 2: Noise floor is measured per-metric from repeated runs, never a constant

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** v1 demands "medição de noise floor" and refuses verdicts from isolated p95. A fixed threshold would be a fabricated constant.

**Choice:** `noise_floor(runs: list[PerformanceRun], metric)` computes `(max - min) / mean` across ≥2 repeated same-subject runs. `perf verdict` accepts `--noise-floor <dir>` pointing at repeated baseline runs; when the measured floor exceeds |delta|, the verdict is `inconclusive` naming both values. With <2 repeats the floor measure is `None` — unproven, and the verdict says so.

**Rationale:** The floor is a property of the measurement environment — it must be measured from runs, not declared in config.

**Alternatives Rejected:**
1. Fixed percentage floor in policy — rejected: invents a constant the spec forbids.
2. Statistical significance tests (t-test etc.) — rejected: heavier machinery than the spec asks; variance floor is the literal requirement and stays deterministic.

**Consequences:**
- Trade-off: coarse measure — named in `limitations`.
- Benefit: honest inconclusive instead of false precision.

---

### Decision 3: `suggest_fix` emits an ActionPlan, and the file diff is data inside it

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** v1: "suggest_fix deve retornar diff ou ActionPlan e nunca aplicar alteração automaticamente."

**Choice:** `perf suggest --case <dir>` reads findings + facts → emits an `ActionPlan` whose steps carry a `proposed_diff` string field (unified-diff text as data). Writing/applying is the existing mutation path (`build endpoint`, policy-gated) — suggest never touches it.

**Rationale:** ActionPlan is the existing contract; embedding the diff as data keeps a single contract for "proposed change" and makes the never-apply boundary structural.

**Alternatives Rejected:**
1. Emit a `.patch` file — rejected: a file invites application; data in a plan keeps the boundary visible.
2. Inline code edits — rejected: violates the spec outright.

**Consequences:**
- Trade-off: ActionPlan needs a `proposed_diff` optional field — additive, backward compatible.
- Benefit: the suggestion is evidence-signed like every other artifact.

---

### Decision 4: New index kinds are derivations, not extractors

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** v1 lists 12 index kinds; 4 exist. Assumption A-001 says existing facts carry the signal.

**Choice:** `index build` derives the 8 new kinds by filtering `inventory.facts` by kind-prefix — no parsing code: `schemas` ← `contract.*`, `dependencies` ← `data.*`, `calls` ← `resilience.http_call`, `tests` ← `test.*`, `iac` ← `infra.*`, `databases` ← `data_access_ir` payload, `findings` ← case findings, `decisions` ← autonomy ledger entries. Empty derivations emit an explicit empty file — absence recorded, never filled.

**Rationale:** Facts are already extracted with provenance; re-parsing would duplicate extraction and risk divergence.

**Alternatives Rejected:**
1. Dedicated per-kind extractors — rejected: duplicates extraction, violates single-source-of-facts.

**Consequences:**
- Trade-off: index granularity = fact granularity (a "call" index is call-site facts, not a full call graph) — named as a limitation.
- Benefit: deterministic, zero new parsers.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/perf/run_store.py` | Create | Append-only run memory + search | @api-capacity-engineer | None |
| 2 | `src/apiforge/perf/noise.py` | Create | Noise-floor measurement over repeated runs | @api-performance-engineer | 1 |
| 3 | `src/apiforge/perf/suggest.py` | Create | findings+facts → ActionPlan | @api-performance-engineer | 1, 2 |
| 4 | `src/apiforge/contracts/core.py` | Modify | `ActionPlan` gains optional `proposed_diff` | @api-contract-architect | None |
| 5 | `src/apiforge/index/build.py` | Modify | +8 derived index kinds | @api-data-access-architect | None |
| 6 | `src/apiforge/autonomy/heal.py` | Create | Self-healing runbook pipeline | @api-resilience-engineer | None |
| 7 | `src/apiforge/autonomy/modes.py` | Modify | `V1_MODE_MAP` reconciliation constant | @api-operations-engineer | None |
| 8 | `src/apiforge/knowledge/loader.py` | Modify | eval `type` closed set (11 values) | @api-test-strategist | None |
| 9 | `tests/labs/matrix.yaml` | Create | Declared tech × case matrix | @api-test-strategist | None |
| 10 | `src/apiforge/cli.py` | Modify | `perf memory`, `perf suggest`, `--noise-floor` on verdict | (general) | 1, 2, 3 |
| 11 | `src/apiforge/dispatch/runner.py` | Modify | dispatch parity for new verbs | (general) | 1, 3, 6 |
| 12 | `src/apiforge/mcp/tools.py` | Modify | MCP parity (read-only verbs) | (general) | 1, 3 |
| 13 | `tests/perf/test_run_store.py` | Create | Memory round-trip + empty-result honesty | @api-capacity-engineer | 1 |
| 14 | `tests/perf/test_noise.py` | Create | Floor math + inconclusive verdict | @api-performance-engineer | 2 |
| 15 | `tests/perf/test_suggest.py` | Create | ActionPlan emitted, repo bytes unchanged | @api-performance-engineer | 3 |
| 16 | `tests/index/test_build.py` | Modify | 12-kind manifest assertions | @api-data-access-architect | 5 |
| 17 | `tests/autonomy/test_heal.py` | Create | Pipeline stages, deny-path, ledger records | @api-resilience-engineer | 6 |
| 18 | `tests/knowledge/` eval type test | Create | Invalid `type` → named refusal | @api-test-strategist | 8 |
| 19 | `tests/labs/test_matrix.py` | Create | Declared cells resolve to real fixtures/evals | @api-test-strategist | 9 |
| 20 | `docs/decisions/ADR-010-autonomy-modes.md` | Create | Mode × class reconciliation | @api-operations-engineer | 7 |
| 21 | `docs/catalog-contract.md` + `README.md` | Modify | New verbs/codes documented | @api-release-guardian | 10-12 |
| 22 | `scripts/check_release.py` | Modify | New AF-* prefixes if any emitted | @api-release-guardian | 10 |

**Total Files:** 22

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @api-capacity-engineer | 1, 13 | Run memory and capacity evidence are its domain (perf verdict/compare playbooks) |
| @api-performance-engineer | 2, 3, 14, 15 | Noise floor and fix suggestions are performance judgments grounded in measured runs |
| @api-contract-architect | 4 | Contract change — additive field on ActionPlan |
| @api-data-access-architect | 5, 16 | Index derivation reads `data.*`/`data_access_ir` facts |
| @api-resilience-engineer | 6, 17 | Self-healing loop is resilience-operational domain |
| @api-operations-engineer | 7, 20 | Mode semantics + the ADR documenting them |
| @api-test-strategist | 8, 9, 18, 19 | Eval vocabulary and lab matrix are test-strategy surface |
| @api-release-guardian | 21, 22 | Docs parity and release-gate surface |
| (general) | 10, 11, 12 | Mechanical wiring into existing CLI/dispatch/MCP tables |

**Agent Discovery:**
- Scanned: `agents/*.md` (repo coordinators — the project's own specialist set, used instead of the agentspec data-engineering roster which has no platform-domain match)
- Matched by: `rule_areas`, playbook verbs, purpose keywords

---

## Code Patterns

### Pattern 1: Verb skeleton (CLI + dispatch parity)

```python
# Existing pattern — every verb: work() closure + _run() + _echo_json()
@perf_app.command("memory")
def perf_memory(
    subject: str | None = typer.Option(None, "--subject"),
    tool: str | None = typer.Option(None, "--tool"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Search persisted PerformanceRuns by declared fields only."""

    def work() -> dict[str, object]:
        from apiforge.perf.run_store import search_runs
        return {"runs": search_runs(root, subject=subject, tool=tool)}

    _echo_json(_run(work), detail_level)
```

### Pattern 2: Honest-absence measure

```python
# Noise floor with insufficient repeats — measure is None, verdict names it
def noise_floor(runs: list[PerformanceRun], metric: str) -> float | None:
    values = [op[metric] for r in runs for op in _ops(r).values() if metric in op]
    if len(values) < 2:
        return None  # floor unproven — never assumed
    return (max(values) - min(values)) / (sum(values) / len(values))
```

### Pattern 3: Configuration Structure

```yaml
# tests/labs/matrix.yaml — declared cells; empty pointers are named, not fabricated
cells:
  - technology: redis
    case: query_without_limit
    fixture: tests/fixtures/redis_app
    eval: redis-valkey/no-ttl-write
  - technology: neptune
    case: unbounded_traversal
    fixture: tests/fixtures/dbaccess_app
    eval: neptune/unbounded-traversal
```

---

## Data Flow

```text
1. `model otel`/report readers produce PerformanceRun payloads
   │
   ▼
2. `perf memory add` persists payload sha256-keyed lines to
   .apiforge/perf/runs.jsonl; `perf memory search` filters declared fields
   │
   ▼
3. `perf compare --repeat-baseline dir/` measures noise_floor from
   repeated same-subject runs; `perf verdict` cites floor on inconclusive
   │
   ▼
4. `perf suggest --case` reads findings → emits ActionPlan (proposed_diff
   as data); never applies — mutation stays behind the existing gate
   │
   ▼
5. `index build` derives 12 kinds from inventory.facts + case findings +
   autonomy ledger — no new extraction
   │
   ▼
6. `autonomy run --runbook self-healing` walks the 8-stage pipeline,
   each transition policy-decided and ledgered; rollback is a named stage
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| None | — | — |

All surfaces are local files and in-process calls; no new external integration.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | run_store round-trip/search filters; noise_floor math + <2-run None; suggest emits valid ActionPlan + no writes; heal deny path; eval-type refusal; matrix coverage test | `tests/perf/test_run_store.py`, `test_noise.py`, `test_suggest.py`, `tests/autonomy/test_heal.py`, `tests/knowledge/`, `tests/labs/test_matrix.py` | pytest | Every new function |
| Integration | index build 12-kind manifest on a real case; CLI verbs end-to-end | `tests/index/test_build.py`, dispatch/MCP surface tests | pytest | Key paths |
| E2E | `perf memory` → `compare --repeat-baseline` → `verdict` inconclusive chain | `tests/perf/` | pytest | AT-001/002/003 |

Every DEFINE acceptance test AT-001..008 maps to at least one test above.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Memory store file corrupt | `AF-PERF-MEMORY-CORRUPT` naming the file + line count | No — file is the record |
| Noise-floor input has <2 runs | `noise_floor=None`, verdict says floor unproven | No |
| Suggest case lacks findings | Empty ActionPlan with `reason` named | No |
| Heal step decision is gate/deny | Step `pending`/`denied` with missing requirements named; runbook halts (supervised) or records skip (continuous) | No |
| eval `type` outside closed set | `AF-KNOW-EVAL-TYPE` refusal naming the value | No |
| Matrix cell lacks fixture/eval | Test failure naming the cell | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `.apiforge/perf/runs.jsonl` | path | `.apiforge/perf/` | Append-only run memory |
| `.apiforge/autonomy/ledger.jsonl` | path | existing | Pipeline transitions append here |

No tunable constants introduced — noise floor is measured, thresholds stay explicit arguments.

---

## Security Considerations

- `perf suggest` never writes outside the evidence receipt — the never-apply boundary is structural (no write call exists in the module).
- Heal pipeline executes only dispatch-table verbs; every stage is policy-decided — no remediation outside policy/runbook coverage, per the spec's own rule.
- `runs.jsonl` stores payload hashes; the payload itself may carry target URLs — store stays local under `.apiforge/`, same as existing state.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Ledger entries per heal stage (decision + missing requirements + output hash) |
| Metrics | `runs.jsonl` line count, noise-floor value in verdict output |
| Tracing | N/A — offline tool; evidence receipts carry sha256 provenance |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_V1_CLOSURE.md`
