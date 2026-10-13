# API Forge — Final Runtime Convergence Baseline

Date: 2026-10-06 (America/Sao_Paulo)
Branch: `codex/evo-final-runtime-convergence`
Base (BASE_SHA): `0bd496b6214ae68f8df59f5a95cce111da914caf` (`main`, clean, synced with `origin/main`)

## Method

The persisted case under `.apiforge/case/` was loaded before analysis. Its
findings are historical fixture findings (`tests/fixtures/orders_agentic`);
`apiforge next-step --phase build` correctly refuses them with
`AF-ROUTING-NO-ROUTE`, so this wave proceeds on the audited source path and
records the refusal instead of forcing a route.

The implementation audit followed the real execution path:
`runtime/supervisor.execute_run` → `runtime/scheduler.run_bounded` →
`governance/recovery`, `runtime/model_router`, `governance/control_plane`,
`trust/plane`, `trust/propagation`, `trust/tools`, `memory/conflicts`,
`memory/store`, `mcp/gateway`, `agentops/inspect`, `agentops/timeline`.

## Environment

| Field | Observed value | Boundary |
|---|---|---|
| branch | `codex/evo-final-runtime-convergence` | local Git state |
| working tree | clean at branch creation | local Git state |
| Python host | `3.14.6` | project declares `>=3.12,<3.13`; the uv project environment is used for all gates — host version is an environment caveat, not a code claim |
| package | `apiforge 0.1.0` | `pyproject.toml` |
| lock | `uv lock --check` PASS | deterministic lock consistent |
| MCP SDK | optional extra not installed in the default env | real-SDK proof (Phase 8) is `DEFERRED_EXTERNAL` unless installed |

## Gate baseline (this wave, fresh runs)

| Gate | Result | Evidence / limitation |
|---|---|---|
| `uv lock --check` | PASS | — |
| Ruff check | PASS | `uv run ruff check src tests` |
| Ruff format | PASS | `1000 files already formatted` |
| mypy | PASS | `no issues found in 561 source files` |
| full pytest | PASS | `1751 passed, 2 skipped` — first attempt showed 4 false failures caused by placing `--basetemp` inside the repo (git-detection tests see the parent `.git`); all 4 pass with an external basetemp; default `%TEMP%` basetemp is permission-denied on this host |
| release gate | PASS | `scripts/check_release.py` |
| SDD registry | PASS after repair | `AF-SDD-UPSTREAM-STALE` on `API_FORGE_STEP11_CONTEXT_QUALITY` was present on `main`; fixed by re-stamping the artifact chain `architecture→plan→build→verify→secure→benchmark→ship` via `apiforge sdd stamp` |
| skills | PASS | `scripts/validate_skills.py` |
| agent mirrors | PASS | `apiforge agents check` — drift `[]` |
| capabilities | PASS | `21/21` verified, no gaps |
| evals / Lab / platform probes | not rerun in Phase 0 | hardening-2 wave recorded green; they are re-executed in Phase 11–12 for this wave's evidence |

## Confirmed defects (drive Phases 1–10)

1. **P0 memory conflict** — `memory/conflicts.py`: preference scoring runs
   before the destructive check, so `risk=destructive` can return
   `prefer_a`/`prefer_b` while `memory/store.query_memory` excludes both
   records. Outcome contradicts the result set.
2. **Recovery dual authority** — `runtime/supervisor.py` (~L1361) re-runs
   `decide_recovery` after `runtime/scheduler` already stored
   `InvocationResult.recovery`.
3. **Recovery actions inert** — `replan`/`fallback`/`escalate`/`stop`
   decisions are recorded but do not change subsequent runtime behavior; no
   recovery receipt exists.
4. **Model router outside the run path** — `route_model_shadow` exists and
   records through `evaluate_route`, but `execute_run` never calls it.
5. **Trust path stops at contracts** — `trust/plane` + `trust/propagation`
   are correct; runtime never annotates tool/model/external outputs, and
   `RoleContextPlan.trust_floor` is not enforced at admission.
6. **MCP target auth ignores risk** — `authorize(target=True)` returns
   `risk_classes=("read_only",)` for any registry target when
   `allowed_targets` contains `"*"`.
7. **AgentOps naming/order** — `cost_coverage` measures `CostVector`
   presence (not monetary cost); ledger rows lack timestamps so no temporal
   ordering or critical path can be derived.
8. **Challenger semantics** — `runtime/shadow` samples capability
   challengers, but no canonical champion/challenger comparison receipt is
   produced.

## Unresolved

- Host Python (3.14.6) is outside the declared `>=3.12,<3.13` range; gates
  run under uv's project environment. Recorded as an environment caveat.
- `next-step` refused the stale fixture case (`AF-ROUTING-NO-ROUTE`) —
  recorded; not a regression.
- Eval, Lab and platform-probe numbers for this wave are produced in
  Phase 11–12, not restated from the prior wave.
