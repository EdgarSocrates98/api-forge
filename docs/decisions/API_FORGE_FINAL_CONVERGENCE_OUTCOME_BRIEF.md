# API Forge — Final Runtime Convergence — Outcome Brief

Wave: `prompt_evo_final_runtime.md` — close the last inconsistencies that
prevented API Forge from operating as **one governed agentic system**, moving
the platform from architecture-driven evolution to evaluation-driven
refinement.

Branch: `codex/evo-final-runtime-convergence`
Baseline: `main @ 0bd496b`
Date: evidence bundle produced on the branch head (`055f889` + phase-12 docs)

## Outcome

All twelve audited gap rows are closed locally. The governed circuit —
Context → Trust → Memory → Routing → Decision Control → Tool Authorization →
Runtime → Recovery → Economy → Observability → AgentOps — is now observable,
receipt-backed and replayable end to end:

- **Memory (P0):** destructive queries that hit fresh contradictions return
  `quarantine`/`exclude_both` *before* preference scoring; the conflict audit
  and excluded records are preserved, so outcome and result set can no longer
  contradict each other.
- **Recovery:** `classify_failure` is a single governed surface; the
  supervisor consumes `InvocationResult.recovery` (never re-decides), then
  executes the canonical action — retry, fallback (`fallback_order`, bounded
  by `max_fallbacks`), replan (`ControlPlane.add_steps` + loop check +
  fresh fingerprint), escalate (`recovery_escalation` human-gate reason) or
  stop — and persists a `RecoveryReceipt/v1` per decision. Depth bounded at
  one (`AF-GOV-RECOVERY-DEPTH`).
- **Model routing:** every governed run emits a `ModelRouteShadowReceipt/v1`
  and a §29 `ShadowRecord` in the decision control plane; the declared
  adapter remains the governing route. Inputs derive only from declared run
  data — scorecards load from a declared, root-confined JSONL.
- **Control plane:** `governance.control_plane` is the sole route-lifecycle
  authority; every promote/demote attempt emits `RouteTransitionReceipt/v1`;
  overlapping runtime helpers documented as nominal, not duplicated, in the
  migration map.
- **Trust/taint:** `plan_roles` admits refs through `TrustUnit` floors and
  `denied_taints` (`AF-TRUST-FLOOR`/`AF-TRUST-TAINT-DENIED`); run artifacts
  enter downstream roles as `model_generated` data — never instruction.
- **MCP tool authorization:** target-path `authorize` is fail-closed and
  risk-aware across all 152 full-surface tools; wildcard target grants
  cannot bypass `allowed_risk_classes`/`denied_tools`.
- **MCP SDK:** real `mcp` 2.3.0 protocol round-trip proof
  (`initialize`/`tools/list`/`tools/call`); server migrated to the v2
  `MCPServer` API; the test skips rather than fakes without the SDK.
- **Champion/challenger:** `ChallengerSide/v1` + `ChallengerComparison/v1`
  persisted per executed challenger over observable fields only;
  `governs=false` contractual.
- **AgentOps:** honest `cost_vector` basis, ledger timestamps
  (`recorded_at`), `timestamp_coverage`, and `critical_path` that stays
  `unresolved` when timestamps are insufficient.
- **Evals/labs:** 26/26 lab catalog coverage with real engine probes;
  security-adversarial corpus 9→16 cases (confused deputy, MCP target
  escalation, instruction laundering, tainted output, destructive memory
  conflict) — all refused or contained; `evals replay` deterministically
  re-decides loop/shadow/tool-authz/trust/recovery anchored by
  `policy_id`/`policy_version`/`policy_hash`. Replay never reproduces model
  text — only the control plane.

## Phase commits

| Phase | Commit | Scope |
|---|---|---|
| 0 | `71368ae` | baseline, ownership, gap matrix |
| 1 | `dee0d2b` | destructive memory conflict semantics |
| 2 | `f25e9bb` | canonical recovery classification |
| 3 | `f496ad8` | governed recovery execution + receipts |
| 4 | `7990659` | model-router shadow in `execute_run` |
| 5 | `235235a` | control-plane convergence + transition receipts |
| 6 | `b61071c` | trust/taint context admission |
| 7 | `2ee7157` | risk-aware MCP target authorization |
| 8 | `ee958a4` | real MCP SDK proof + v2 migration |
| 9 | `1ada789` | champion/challenger comparison receipt |
| 10 | `90d2455` | AgentOps semantic hardening |
| 11 | `055f889` | labs/evals + deterministic decision replay |
| 12 | *this commit* | release proof, docs parity, outcome brief |

## Proof (local gates)

- `python scripts/check_release.py` — **PASS**
- `apiforge sdd check --root docs/sdd` — **ok, zero refused/unresolved**
- `ruff check` + `ruff format --check` on changed files — **clean**
- `mypy src/apiforge` — **no issues in 562 source files**
- `pytest tests/` — **1805 passed, 1 skipped** (explicit external basetemp)
- `evals security-adversarial` — 16/16 (10 refusals = contained attacks)
- `evals memory-evals` — 9/9
- `evals economy-hardening` — all cases passed
- `evals agentic-quality` — passed, accuracy 1.0 on all three profiles
- `evals replay` — deterministic report, zero unresolved

## Gaps / unresolved

- **Basetemp caveat:** the default Windows basetemp (`pytest-of-edgar`) was
  unwritable and an in-repo basetemp leaks the parent `.git` into
  git-discovery fixtures (false `test_delta_refusals` failure) — the 1805/1
  result was produced with `--basetemp` outside the repository.
- **Transient Windows rename flake** (`run.json.tmp` replace, WinError 5)
  observed twice under parallel I/O; passes on retry — environment artifact,
  not a deterministic defect.
- **Format drift:** ~35 pre-existing files (archived SDD docs, eval
  fixtures intentionally unformatted) fail `ruff format --check` on the
  baseline too; untouched — they are fixtures, not production code.
- **External/provider claims:** none made — MCP proof is local SDK
  round-trip; no cloud, provider or live-database evidence is claimed.
- **PR lifecycle:** branch pushed; PR state left to the dedicated CI
  boundary — no PR status is asserted here.

## Next human action

Review the branch, run the CI gate, and open the PR through the repository's
`open-green-pr` boundary if accepted. Promotion of shadow routes remains a
control-plane decision over accumulated evidence — this wave deliberately
changes no governing authority.
