# API Forge Evolution 1 — Outcome Brief

Date: 2026-10-04  
Status: REVIEW — the governed local evolution is shipped; external/runtime
claims remain unresolved by policy.

## Outcome

Four additive waves were delivered from the existing deterministic, offline-first
platform. Every wave uses closed v1 contracts, the SDD hash cascade, local
append-only artifacts, CLI/MCP service parity, focused tests and a full-suite
regression before its commit.

| Wave | Capability | Commit | Evidence |
|---|---|---|---|
| 1 | governed memory, blackboard and semantic checkpoints | `17aa3e8` | `19 passed, 1 skipped` focused; full suite `1427 passed, 2 skipped` |
| 2 | hierarchical task/phase/role/tool budget governor | `8f23444` | `22 passed, 1 skipped` focused; full suite `1430 passed, 2 skipped` |
| 3 | local OTel-shaped agent/tool spans and sensitive-key gate | `876d1d9` | `19 passed, 1 skipped` focused; full suite `1433 passed, 2 skipped` |
| 4 | fail-closed decision governor and approval audit | `5837cd5` | `25 passed, 1 skipped` focused; full suite `1436 passed, 2 skipped` |

The final independent repository evidence is `1436 passed, 2 skipped`; Ruff,
full mypy, the release gate and the SDD check all passed. Full mypy was run in
the declared Python `3.12.13` environment with MCP `1.30.0` (`mcp>=1.12,<2`):
`Success: no issues found in 486 source files`. The host checkout is clean.

## Independent evaluation receipts

The repository holdout/economy evaluations also passed without external model
or provider calls:

- `evals economy-hardening --corpus evals/corpus/economy-hardening`: `18`
  cases, all six gates passed (`budget`, `budget_invariant`, `delta`, `path`,
  `phase`, `tokens`). The refusal, degraded, unresolved and protected-overrun
  cases were preserved and evaluated as expected.
- `evals agentic-quality --corpus evals/corpus/agentic-quality
  --min-accuracy 1.0`: `6` cases, accuracy `1.0` for `economy`, `balanced` and
  `deep`, all gates passed, every case answered and no run blocked. The
  evaluator recorded corpus SHA-256
  `cf30554dbb9069922d529fa93878f17150e95f857876efab892bac9effa65439`.

## Prompt coverage

| Prompt concern | Result |
|---|---|
| memory plane / blackboard | first-class `Memory*` and `Blackboard*` contracts and stores |
| semantic checkpoint / recovery | independent checkpoint state under `.apiforge/runtime/checkpoints` |
| hierarchical budgets / token economics | `AgenticBudgetPlan`, pre-append admission, observed-token-only policy |
| trust / taint / evidence | memory promotion gates, blackboard taint, refusal codes and provenance |
| security / decision control | `DecisionRequest`, `ApprovalGate`, `DecisionGateResult`, default-deny mutation |
| observability | local `AgentSpan` trace/run/task evidence; no exporter claim |
| routing / retrieval / tool surface / MCP | existing deterministic surfaces retained and new projections added |
| evals / AgentOps / knowledge freshness | existing repository capabilities remain in place; no new provider execution |

## Unresolved and human action

- Security scanners and production performance benchmarks were not executed by
  these local waves. No throughput, token-savings, cloud posture or production
  safety claim is made.
- Live telemetry export, external mutation, model calls, A2A/provider
  integration and automatic promotion remain explicit policy boundaries.

## Research inputs

- Spark Forge's public evidence-first architecture informed the choice to keep
  cases, append-only state, blackboard decisions and economy receipts local and
  evidence-bound: <https://github.com/EdgarSocrates98/spark-forge-aws>.
- MCP's host/client/server and human-control model informed the refusal and
  approval boundary: <https://modelcontextprotocol.io/specification/2025-06-18>.
- OpenTelemetry's agent span conventions informed the `invoke_agent` and
  `execute_tool` operation vocabulary, while the implementation remains local:
  <https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md>.

## Next

Run the declared dependency matrix, security corpus and benchmark/holdout waves
under an explicitly approved environment. Promote to DONE only when those
independent receipts and the external integration boundaries are resolved.
