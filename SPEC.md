# SPEC.md — API_FORGE_V1_CLOSURE

Source: .claude/sdd/features/DESIGN_API_FORGE_V1_CLOSURE.md (linted PASS)

## §G
close 9 residual v1 gaps: perf memory, noise floor, suggest_fix, 12 index kinds, self-heal pipeline, eval vocabulary, lab matrix, autonomy reconciliation, rollback

## §C
- deterministic, local-first, offline
- no fabricated measures; absence recorded, never filled
- suggest_fix emits ActionPlan/diff; never mutates repo
- perf semantics kept: RPS≠TPS, saturation invalidates, no interpolation, missing baseline named
- every verb: CLI + dispatch + MCP read-only parity
- pytest + ruff + mypy + release gate green at end

## §I
- `perf memory add|search` — .apiforge/perf/runs.jsonl
- `perf suggest --case` — ActionPlan JSON out
- `perf verdict --noise-floor <dir>` — repeated baseline runs dir
- `index build` — manifest with 12 kinds
- `autonomy run --runbook self-healing` — 8-stage pipeline
- `ActionPlan.proposed_diff` — optional str field, additive
- `evals.yaml` — `type` field, closed 11-value set
- `tests/labs/matrix.yaml` — technology × case → fixture/eval
- `autonomy/modes.py` — `V1_MODE_MAP` constant

## §R
| id | fact | source |
|----|------|--------|
| R1 | 3 modes + policy classes cover v1 5-mode semantics; V1_MODE_MAP + ADR-010 make it auditable | design D1 |
| R2 | noise floor = (max-min)/mean over ≥2 same-subject runs; <2 → None, unproven | design D2 |
| R3 | suggest emits ActionPlan; proposed_diff is data inside; module has no write call | design D3 |
| R4 | 8 new index kinds derive from existing facts; empty → explicit empty file | design D4 |

## §V
- V1 suggest_fix returns ActionPlan or diff; no write path exists in module
- V2 noise_floor measured, never constant; <2 runs → None named unproven
- V3 |delta| < measured floor → verdict `inconclusive` naming both values
- V4 index manifest has exactly 12 kinds; new kinds are fact derivations, no parsers
- V5 heal stages: detect→explain→propose→authorize→execute→verify→compare→accept|rollback; each transition policy-decided + ledgered
- V6 heal executes dispatch-table verbs only; deny names missing requirements
- V7 eval `type` outside 11-value set → named refusal `AF-KNOW-EVAL-TYPE`
- V8 every matrix cell resolves to real fixture/eval or is a named gap
- V9 every new verb appears in CLI + dispatch + MCP (read-only) + surface tests
- V10 empty derivations → explicit empty output; absence never filled

## §T
| id | status | goal | cites |
|----|--------|------|-------|
| T1 | x | perf/run_store.py: append-only runs.jsonl + search subject/tool/since | V10,I.runsjsonl |
| T2 | x | perf/noise.py: noise_floor per metric + verdict --noise-floor wiring | V2,V3 |
| T3 | x | ActionPlan.proposed_diff + perf/suggest.py emits plan, never writes | V1,V9 |
| T4 | x | index/build.py: +8 derived kinds, 12-kind manifest | V4,V10 |
| T5 | x | autonomy/heal.py: 8-stage pipeline over policy.decide + ledger | V5,V6 |
| T6 | x | V1_MODE_MAP + ADR-010 | V5,R1 |
| T7 | x | eval type closed-set validation in knowledge loader | V7 |
| T8 | x | tests/labs/matrix.yaml + coverage test | V8 |
| T9 | x | CLI + dispatch + MCP wiring + docs for all new verbs | V9 |
| T10 | x | full verify: pytest ruff mypy release gate | all |

## §B
| id | date | cause | fix |
|----|------|-------|-----|
