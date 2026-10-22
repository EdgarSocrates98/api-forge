# Evals taxonomy & verification — api-forge (install-2.0 §7, lf-0038)

API Forge's eval surface is large and native: ~30 `apiforge evals <suite>`
verbs plus the task/verification machinery (`task holdout`, `task verify`,
`verify plan`, `verify escalate`, `evals gate`, `evals replay`). Cycle 5 does
not reimplement them — it classifies them (§7.1), maps the §7.2 conceptual
ops onto the real verbs, enforces §7.3, and documents the §7.4 flow.

The declared catalog lives in `src/apiforge/evals/catalog.py`
(`apiforge.evals.catalog.SUITES`) and is persisted into the
`forge/context/v1` manifest (`eval_suites` + `discovery.ops`) by
`install`/`_context_manifest`.

## 7.1 — Classified inventory (33 suites)

| Kind | Count | Suites |
|---|---|---|
| developer | 13 | `validate`, `economy`, `economy-matrix`, `economy-extras`, `economy-hardening`, `economy-freshness`, `cache`, `selective-agentics`, `tool-economy`, `memory-evals`, `token-economics`, `knowledge-drift`, `agentops` |
| runtime-decision | 10 | `economy-routing`, `model-routing`, `retrieval`, `control-plane`, `agent-governor`, `security-adversarial`, `replay`, `gate`, `task-holdout`, `task-verify` |
| output-verification | 5 | `agentic-quality`, `context-quality`, `graph-quality`, `trace-grading`, `frontier` |
| host-conformance | 5 | `tool-surface`, `forge-protocol`, `agent-routing`, `telemetry-otlp`, `live` |

Classification rule: *developer* suites gate apiforge internals on
deterministic corpora; *runtime-decision* suites judge decisions the
runtime/control-plane makes (routing, lifecycle, adversarial answers, gates,
task proofs); *output-verification* grades produced artifacts (quality,
traces, frontier); *host-conformance* checks the host/provider surface
(tool surface, Forge protocol, agent routing mirrors, OTLP, live provider
tiers).

## 7.2 — Conceptual ops → real verbs

| Op | Discovery command | Real verb |
|---|---|---|
| `evals.list` | `evals-catalog` | `apiforge evals catalog` (new thin adapter — classified suites, metadata only) |
| `evals.describe` | `evals-describe` | `apiforge evals describe <suite>` (new — sealed paths as sha256, never answers) |
| `evals.run` | `evals-run` | `apiforge evals run <suite> [--set name=value]` (new — dispatches the suite's native runner; `AF-EVALS-RUN-INPUT` when a declared input is missing) |
| `evals.result` | `evals-result` | `apiforge evals result --report <file>` (new — reads a persisted report back with schema + environment marker) |
| `verification.plan` | `verify-plan` | `apiforge verify plan --changed <f> --risk <r>` (existing — risk ladder + impacted tests) |
| `verification.run` | `task-verify` | `apiforge task verify <id> --project --contract [--manifest]` (existing — executes proof checks, persists the VerificationRecord) |

`evals list` (per-file case listing) and the ~30 suite verbs remain native
and untouched; the four new verbs are discovery/dispatch adapters, not a
second engine.

## 7.3 — Security rules enforced

- **Holdout answers never exposed.** `evals catalog`/`describe` return ids,
  kinds, environments, declared inputs and sealed-path digests only.
  `describe` reports `sealed` baselines/holdouts as *path + sha256 + count*
  with the marker `sealed — expected answers/baselines never inlined into
  agent-facing output`. A test reads a real secret out of
  `evals/corpus/agent-routing/holdout.json` and proves it never reaches
  describe output.
- **Executor ≠ evaluator.** `evals run` dispatches the declared runner;
  verdicts come from the runner's own contract fields (`passed`/`decision`),
  never from the adapter grading itself. Holdout evaluation stays inside
  `verification.holdout` — expected detections live in the sealed manifest,
  not in agent-facing payloads.
- **Baselines hash-protected.** `describe` pins every declared sealed file
  to sha256; `evals result` records `report_sha256`. The native gates keep
  their own protections (`AF-EVALS-ECONOMY-BASELINE-STALE`,
  `AF-EVALS-BASELINE-MISMATCH`, `AF-EVALS-GATE-MISMATCH`) — unauthorized
  drift is refused upstream.
- **No destructive tests, no cloud mutation.** All runners are local,
  deterministic and read-only over fixtures; `task holdout` applies only
  declared allowlisted local mutations. No eval performs a cloud/provider
  mutation.
- **Simulated ≠ real.** Every suite carries `environment`:
  `simulated` for deterministic fixture/corpus evidence,
  `deferred-external` for `live` (provider tier is human-gated via
  `live_evals` — never fabricated). Results re-emit the marker so a host
  cannot confuse fixture proof with real-environment attestation.

## 7.4 — Plan → run → evidence

```text
apiforge verify plan --changed src/... --risk medium      # select (never executes)
apiforge evals run agentic-quality                        # execute a declared suite
apiforge evals result --report agentic-quality.json       # read evidence back
apiforge task verify <task> --project P --contract C      # independent proof → VerificationRecord
```

- `verify plan` selects applicable checks deterministically and escalates an
  empty selection to the full suite (`verification/selection.py`).
- `verify escalate` adjudicates evidence stepwise (static → test → read-only
  runtime); exhausted evidence stays `unresolved`/`inconclusive` — never
  upgraded to a pass.
- `task verify` runs the authorized proof checks (project/contract checks +
  optional holdouts) and persists a `VerificationRecord` with `verdict`,
  `checks`, `evidence` and `gaps`.
- Verdicts stay explicit: `pass`/`fail`/`blocked`/`inconclusive`/`unresolved`;
  the conclusion is proportional to evidence by construction.

## 7.5 — Agent contracts

`agents/*.md` is the only hand-edited source (25 coordinators); mirrors in
`.claude/agents`, `.agents/agents`, `.codex/agents` are generated by
`apiforge agents sync` and gated by `apiforge agents lint` / `agents check` /
`agents references`. Every coordinator references the canonical
`AGENT_PROTOCOL.md` (`Follow \`AGENT_PROTOCOL.md\`.`) — the protocol is
referenced, never duplicated per agent.

## Gates

Focused: `pytest tests/test_evals_cycle5.py tests/test_discovery_ops.py -q`.
Long suites (full pytest, the eval corpora themselves) are deferred to CI.
