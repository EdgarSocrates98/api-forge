# API Forge — Evo Convergence Baseline

Date: 2026-10-05 (America/Sao_Paulo)
Branch under work: `codex/evo-convergence`
Base commit: `daae355a78664befabbc4321eeefa5c049ba37cb`

## Scope and method

This baseline was collected from the repository state above after reading
`AGENT_PROTOCOL.md`, the real runtime path, policies, contracts, tests, eval
corpora and CI workflows. The prompt's previous-wave claims were treated as
reported input and revalidated with local commands.

The authoritative evidence is the command output from this run and the
persisted `.apiforge/case/` artifacts. The case's pre-existing contract
findings remain a separate fixture case; they do not describe the API Forge
repository itself.

## Gate snapshot

| Gate | Result | Evidence / limitation |
|---|---|---|
| `git` baseline | observed | `git show -s --format=... HEAD` |
| `apiforge next-step` | observed | dominant area `CONTRACT`, `api-governance-reviewer`, `discover` |
| capabilities | PASS | `apiforge capabilities verify`: 21 verified, no gaps |
| agent mirrors | PASS | `apiforge agents check --root .`: drift `[]` |
| SDD registry | PASS | `apiforge sdd check --root docs/sdd`: 77 features, no refusals/gaps |
| release gate | PASS | `python scripts/check_release.py` |
| mypy | PASS | strict, 557 source files |
| skills | PASS | `scripts/validate_skills.py`: ok |
| platform probes | PASS local fixture tier | 6 vertical probes passed; provider/deployment/production claims remain external |
| MCP audit | PASS with declared exception | 151 tools, no findings, 1 accepted overlap; oversized output needs benchmark sample |
| supply-chain audit | PASS with unresolved | CVE/advisory feed and pip check in uv-only environment unresolved |
| full pytest on host default temp | INCONCLUSIVE | 906 passed, 2 skipped, 1 failed, 800 setup errors caused by `WinError 5` scanning `%TEMP%\\pytest-of-edgar` |
| full pytest with controlled basetemp | required | rerun in the verify wave using an isolated host path outside the repository |

`ruff check .` and `ruff format --check .` include adversarial graph-quality
fixtures and report fixture-only violations. CI intentionally scopes these
gates to `src tests`; that scope is the release gate used below. Fixture
inputs are not formatted or linted as shipped Python.

## Initial runtime assessment

The repository already contains substantial implementations for context,
trust, economy, governance, control plane, retrieval, memory, telemetry,
AgentOps, MCP, Forge Protocol, evals, lab and supply-chain surfaces. The
remaining problem is convergence: several primitives exist as parallel
modules or projections while `execute_run()` still owns legacy decisions.

Confirmed P0 defects:

1. AgentOps asks for `context_duplicates` and `context_stale`, while the
   Context Quality Engine emits `duplicate_context_ratio` and
   `stale_context_ratio`.
2. AgentOps security aggregation reads a legacy boolean `allowed`, while the
   Decision Gate contract is tri-state `outcome: allow|review|block`.
3. AgentOps model calls are counted from Token Ledger rows, which conflates
   model calls, token entries, provider attempts and latency.

## Non-goals for the baseline

No provider, cloud, database, GitHub mutation, merge, deploy or live-model
call was performed. Such claims remain `DEFERRED_EXTERNAL` until a dedicated
read-only adapter or external receipt exists.

