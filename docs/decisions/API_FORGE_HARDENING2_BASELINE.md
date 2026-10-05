# API Forge — Runtime Convergence Hardening II Baseline

Date: 2026-10-05 (America/Sao_Paulo)
Branch: `codex/evo-hardening2-convergence`
Working base: `eb6bab9483e611a3884e8db870b196b5818ee979`
Observed `origin/main`: `a732725fbf4ae58b697fbe04d1ecd28b012530e0`

## Method

The existing API Forge case was loaded before analysis and `apiforge
next-step` was run. The historical contract findings in that case point at
`tests/fixtures/orders_agentic`; they are retained as a separate case and do
not describe this platform wave. The implementation audit then followed the
real execution path through `runtime.supervisor`, `runtime.scheduler`,
governance, retrieval, AgentOps, trust and MCP.

## Environment

| Field | Observed value | Boundary |
|---|---|---|
| branch | `codex/evo-hardening2-convergence` | local Git state |
| working tree | clean before this wave | local Git state |
| Python host | `3.14.6` | project declares `>=3.12,<3.13`; execution uses the project uv environment where available |
| package | `apiforge 0.1.0` | local package metadata |
| lock | `uv lock --check` passed | local lock integrity |
| MCP SDK | optional package not installed in the default environment | MCP server proof remains local/static unless the optional extra is installed |

## Gate baseline

| Gate | Result | Evidence / limitation |
|---|---|---|
| `uv lock --check` | PASS | deterministic lock is consistent |
| Ruff check | PASS | `uv run ruff check src tests` |
| Ruff format | PASS | `980 files already formatted` |
| mypy | PASS | strict check over `557` source files |
| full pytest | PASS | controlled basetemp: `1723 passed, 2 skipped` |
| release gate | PASS | `scripts/check_release.py` |
| skills | PASS | `scripts/validate_skills.py` |
| agent mirrors | PASS | `apiforge agents check --root .`, drift `[]` |
| capabilities | PASS | `21/21` verified, no gaps |
| SDD registry | PASS | `77` existing features, no refusals/unresolved |
| platform probes | PASS local fixture tier | six local verticals; provider/deployment/production claims remain external |
| MCP audit/benchmark | PASS with declared limits | static surface audit; usefulness and live protocol behavior are not inferred |
| Lab catalog | PASS | `13/13` scenarios covered by current catalog, with local-only semantics |
| retrieval eval | PASS | cost-rate and graph freshness remain unresolved in the corpus |
| AgentOps eval | FAIL | `inspect-sections`: model calls are `None` where corpus expects one |
| model-routing eval | FAIL | `deep-task-selects-strongest`: selection is `None` |
| context-quality eval | PASS | unresolved metrics remain explicit, including useful facts |
| memory eval | PASS | `9/9` cases |
| security-adversarial eval | PASS | `9/9`, no escaped cases; this is declared threat-case coverage, not a production security claim |

## Confirmed implementation gaps

1. `execute_run()` calls `check_loop()` with only the current strategy
   fingerprint; the detector cannot observe a repeated trajectory.
2. `run_bounded()` owns a generic retry loop before recovery governance
   classifies the failure.
3. AgentOps context token reporting uses `observed_tokens or 0`, collapsing
   unobserved usage into an observed zero.
4. Adaptive retrieval ranks with hybrid/rerank calculations but retains the
   old `Passage.score` as the sufficiency input; L4 checks `selected_pack`
   instead of graph-depth provenance.
5. The current model-routing corpus has an observed selection regression that
   must be fixed without promoting shadow routing to authority.

## Research inputs

- [MCP 2026-07-28 release notes](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
  establish the modern `server/discover` path, stateless request semantics,
  cache hints and header/body agreement requirements.
- [MCP specification changelog](https://modelcontextprotocol.io/specification/draft/changelog)
  states that list results should be deterministic and that modern transport
  headers must agree with the request body.
- [OpenTelemetry GenAI observability](https://opentelemetry.io/blog/2026/genai-observability/)
  supports keeping agent, model and tool spans plus observed token fields as
  separate evidence dimensions.

## External limits

Live providers, cloud/database/broker mutation, GitHub CI runner health,
production SLOs, vulnerability-feed freshness and production MCP deployment
remain `DEFERRED_EXTERNAL` or `UNRESOLVED` until independent receipts exist.
