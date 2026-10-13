# Plan 15 — Assisted modernization: `plan strangler`

**Goal:** `plan strangler --baseline facts_a.json --candidate facts_b.json`
compares two code inventories' `code.route` facts and emits a deterministic
cut plan: each baseline route is `migrated` (candidate serves method+path),
`missing` (cut blocker), or `stale` (unreachable in baseline); candidate-only
routes are `added` (additive, not a cut dependency). Deeper parity is named
as required evidence, never claimed.

- [ ] T1: `plan/strangler.py` + `plan strangler` verb + `AF-PLAN-*` codes
- [ ] T2: tests + docs/gate parity
