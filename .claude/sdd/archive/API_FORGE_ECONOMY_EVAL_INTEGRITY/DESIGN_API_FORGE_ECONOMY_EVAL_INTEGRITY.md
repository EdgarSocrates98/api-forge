# DESIGN: API Forge Economy Hardening 2 — Eval Integrity

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EVAL_INTEGRITY |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_EVAL_INTEGRITY.md](./DEFINE_API_FORGE_ECONOMY_EVAL_INTEGRITY.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
E1 ─ certification semantics
  evals/agentic_quality.run_agentic_quality(corpus, responses_dir, min_accuracy=1.0, baseline=None)
      gates: <p>_quality_floor (acc >= min) · <p>_not_below_deep · <p>_not_below_baseline · answered · not blocked
      report: min_accuracy, baseline_sha256, baseline_accuracy
  rules/token_eligibility.yaml ─> economy/run_ledger.is_token_eligible(row)
      token_coverage(rows) counts eligible rows only; measured rows always eligible
  run_ledger.persist_failures(root, run_id=None) ─ filters marker rows by run_id
      stats(run_id): persist_failures_for_run / persist_failures_global; unresolved only for the run's own failures

E2 ─ oracle on production paths + explicit path confinement
  evals/hardening.py
      budget ─> analyzed fixture ─> runtime.role_context.plan_roles(...) (contract validators run)
                + negative case: RoleContextPlan above envelope must raise
      delta  ─> analyzed fixture ─> context.delta.build_delta(changed=[...]) ─> status / codes
  security/source_paths.confine_dir(value, root) ─> case dir inside AllowedRoots or refuse
      used by build_delta(case_dir), build_capsule(case), evidence.resolve(case_dir)
  context/delta._normalize ─> resolve_allowed_source; refused --changed item ─> unresolved, never read
```

---

## Key Decisions

### D1: Floor + baseline gates

**Choice:** `min_accuracy: float = 1.0` (0–1) and `baseline: Path | None`. Baseline must be a report with `schema == "apiforge/agentic-quality-eval/v1"` and an `accuracy` mapping; otherwise refuse `AF-EVALS-BASELINE-INVALID` (field `baseline`, unlock "pass a report produced by `evals agentic-quality --out`" — the CLI prints JSON, so the unlock names redirecting stdout). Gates per profile: `quality_floor`, `not_below_deep` (economy, balanced), `not_below_baseline` (only when a baseline is given). `--min-accuracy` outside [0,1] → `AF-EVALS-INPUT-INVALID`.
**Rejected:** relative-only gates (the bug).

### D2: Declarative token eligibility

**Choice:** `rules/token_eligibility.yaml`:
```yaml
schema: apiforge/token-eligibility/v1
verb_prefixes: ["runtime role:", "provider", "transcript"]
```
`is_token_eligible(row) = row.cost.observed_tokens is not None or row.verb.startswith(prefixes)`. `token_coverage` denominator = eligible rows; zero eligible → `unresolved`. Malformed rule → `AF-ECONOMY-TOKEN-RULE-INVALID`.
**Rejected:** all rows eligible (pessimistic false partial).

### D3: Run-scoped persist failures

**Choice:** marker lines already carry `run_id`; `persist_failures(root, run_id=None)` counts all lines or only matching ones. `stats(run_id=R)` reports `persist_failures_for_run` (R only) and `persist_failures_global`; `unresolved` includes `AF-ECONOMY-LEDGER-PERSIST` only when the scoped count > 0 (scope = run filter when given, else global). `persist_failures` key kept as the scoped count for compatibility.

### D4: Hardening oracle uses production code

**Choice:** budget cases analyze `tests/fixtures/economy_payments/fastapi` once (as `evals/extras.py` does), create a sealed TaskSpec with `target=POST /payments`, call `plan_roles(root, spec, roles, context_bytes=...)` and pass when the plan validates and `total_bytes <= context_bytes`; one case builds an over-envelope `RoleContextPlan` and passes only if `ValidationError` is raised. Delta cases call `build_delta(root, changed=[path])` on the analyzed fixture and compare `status` and the presence of `AF-DELTA-UNMAPPED-SOURCE`. `_runtime_path` and the pool arithmetic leave the eval.
**Consequence:** the eval needs `--repo-root` (default `.`) to find the fixture, like `economy-extras`.

### D5: Explicit paths confined

**Choice:** `confine_dir(value, root) -> Path` in `security/source_paths.py` (uses `resolve_allowed_source` with `AllowedRoots.for_project(root)`, raises `SourcePathError` → surfaced as `AF-PATH-OUTSIDE-ROOT` with field `case_dir` and the resolver unlock). `build_delta`, `build_capsule`, `evidence.resolve` call it when a case dir is given. `_normalize` resolves each `--changed` item; refused items are dropped from `paths` and appended to `unresolved` via `SourcePathError.note()`; `_mentions` therefore never reads them. Delta status: a refused changed item is blocking (`unresolved`), since impact of an unknown file cannot be judged.

---

## File Manifest

| # | File | Action | Wave |
|---|------|--------|------|
| 1 | `src/apiforge/evals/agentic_quality.py` | Modify | E1 |
| 2 | `src/apiforge/rules/token_eligibility.yaml` | Create | E1 |
| 3 | `src/apiforge/economy/run_ledger.py` | Modify | E1 |
| 4 | `src/apiforge/cli.py`, `src/apiforge/mcp/tools.py` | Modify (`--min-accuracy`, `--baseline`) | E1 |
| 5 | `tests/economy/test_eval_integrity.py` | Create | E1/E2 |
| 6 | `src/apiforge/evals/hardening.py`, `evals/corpus/economy-hardening/*` | Modify | E2 |
| 7 | `src/apiforge/security/source_paths.py` | Modify (`confine_dir`) | E2 |
| 8 | `src/apiforge/context/delta.py`, `context/gateway/capsule.py`, `evidence/resolve.py` | Modify | E2 |
| 9 | `docs/catalog-contract.md`, threat model EN/PT-BR, economy guide EN/PT-BR, README rows, `docs/sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/` | Modify/Create | E1/E2 |

---

## Testing Strategy

| Test | Proves |
|------|--------|
| all-wrong temp corpus ⇒ `passed=false` | D1 floor (fails on the old gate) |
| baseline 1.0 vs candidate corpus 0.5 ⇒ baseline gate false; invalid baseline ⇒ refusal | D1 baseline |
| deterministic None + provider 1000 + role 500 ⇒ complete 1500; only deterministic ⇒ unresolved | D2 |
| run-A failure, stats(run_id=B) clean | D3 |
| hardening eval passes; monkeypatched `plan_roles` returning oversized budgets makes it fail | D4 oracle is real |
| `build_delta(changed=["../secret.py"])` never opens the file (monkeypatched `_mentions` spy) and reports AF-PATH-OUTSIDE-ROOT; out-of-root `case_dir` refused in delta, capsule, evidence | D5 |

---

## Error Handling

| Code | When |
|------|------|
| `AF-EVALS-BASELINE-INVALID` | baseline missing/non-JSON/wrong schema |
| `AF-EVALS-INPUT-INVALID` | `--min-accuracy` outside [0,1] |
| `AF-ECONOMY-TOKEN-RULE-INVALID` | malformed `token_eligibility.yaml` |
| `AF-PATH-OUTSIDE-ROOT` | `--changed` item (unresolved) or case dir (refusal) outside roots |

---

## Next Step

**Ready for:** `/agentspec:workflow:build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_EVAL_INTEGRITY.md`
