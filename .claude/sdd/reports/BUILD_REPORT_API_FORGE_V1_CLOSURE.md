# Build Report — API_FORGE_V1_CLOSURE

Status: **Complete** · Date: 2026-09-22 · Spec: `SPEC.md` (§T1–T10 all `x`)

## Tasks

| §T | Commit | What landed | Verification |
|----|--------|-------------|--------------|
| T1 | `89f7d16` | `perf/run_store.py` — append-only `.apiforge/perf/runs.jsonl`, payload hash, `search_runs` filters declared subject/tool/since, corrupt line → `AF-PERF-MEMORY-CORRUPT` | `tests/perf/test_run_store.py` (5) |
| T2 | `3ba0e5a` | `perf/noise.py` — `(max−min)/mean` floor, <2 runs → `None`; `compare_runs`/`verdict` accept `repeat_baselines`; deltas inside the floor suppressed, unproven floor named | `tests/perf/test_noise.py` |
| T3 | `10404fb` | `ActionStep.proposed_diff` field + `perf/suggest.py` — findings × catalog remediation → ActionPlan, `remediate` verb is undispatchable by design; module has no write path | `tests/perf/test_suggest.py` (4, incl. repo-bytes-unchanged) |
| T4 | `b26d089` | `index/build.py` — 12 kinds: 4 extracted + `schemas`, `dependencies`, `calls`, `tests`, `iac`, `databases`, `findings`, `decisions` derived from facts/ledger only; `AF-INDEX-DECISIONS-CORRUPT` | `tests/index/test_index.py` |
| T5 | `6bc0fdf` | `autonomy/heal.py` — `detect→explain→propose→authorize→execute→verify→compare→accept\|rollback`; every stage ledgered (`heal.stage`), `authorize` through `decide()`, snapshot/restore of `--writable-path` byte-verified | `tests/autonomy/test_heal.py` |
| T6 | `69fbd71` | `V1_MODE_MAP` (recommend→observe, sandbox/approved→supervised); `set_mode` ledgers the `requested` v1 name; ADR-010 | `tests/autonomy/test_modes.py` (24 in suite) |
| T7 | `7ceb4be` | Closed 11-value eval `type` in every shipped `evals.yaml`; unknown type → `AF-KNOW-EVAL-TYPE` | `tests/knowledge/test_packs.py` (10, 37 packs) |
| T8 | `29eddf9` | `tests/labs/matrix.yaml` — 12 technologies × 16 cases = 192 cells; 21 backed by real fixtures/evals, rest named gaps | `tests/labs/test_matrix.py` (4) |
| T9 | `249cea1` | CLI `perf memory add|search`, `perf suggest`, `--repeat-baseline` on compare/verdict, `autonomy heal`, `index build --findings`; dispatch verbs `perf memory search`/`perf suggest` + `repeat_baseline` ctx; MCP `perf_memory_search`, `perf_suggest`, `repeat_baseline` params; catalog-contract + README + gate prefixes (AF-HEAL, AF-KNOW, AF-SCENARIO, AF-INDEX, AF-INPUT, AF-OTEL now scanned) | MCP surface test + smoke runs |
| T10 | `b0b71a0` | Full suite + gates | 627 passed / 1 skipped, ruff clean, mypy clean (155 files), `check_release.py` PASS |

## Fixes found during build (backprop candidates)

- `perf suggest` / `heal` / dispatch: raw `ValidationError` escaped error envelope on malformed findings — now `AF-PERF-SUGGEST-INPUT` / `AF-HEAL-FINDINGS-INVALID`.
- Heal stage 8 renamed `resolve` → literal `accept`/`rollback` per §V5.
- Gate prefix list was missing 6 emitted prefixes — registering them surfaced 4 undocumented codes (`AF-INDEX-DECISIONS-CORRUPT`, `AF-INPUT-*`); now documented.

## Invariants verified

V1 (suggest never writes) · V2/V3 (floor measured or unproven) · V4 (12 derived kinds) · V5/V6 (stages policy-decided + ledgered) · V7 (closed eval types) · V8 (matrix declares or names) · V9 (CLI/dispatch/MCP parity) · V10 (append-only, hash-backed, unresolved stays unresolved).

## Post-build

`graphify update .` rebuilt: 5075 nodes, 9700 edges, 653 communities.
