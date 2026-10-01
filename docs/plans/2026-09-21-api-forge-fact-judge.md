# Plan 11 — Executable rules over facts (`judge facts`)

**Goal:** Close plans 7/8 for real — `test.*`/`sec.*` facts become judgeable: catalog rules gain an optional closed `check` block (`kind`, `path`, `op`, `value`); `judge facts --facts f.json` emits findings with `fact_id` evidence, never prose.

- [ ] T1: `RuleMeta.check` (`RuleCheck{kind,path,op,value}`, ops `gt|ge|eq|ne|present`) + catalog additions (AF-TEST-201/202/203, AF-SEC-101/102/103) — thresholds live in the rules, citable
- [ ] T2: `rules/fact_judge.py` — dotted path into measures/attrs; confirmed finding per match, evidence=[fact_id]
- [ ] T3: `judge facts --facts <f.json>` verb + tests + docs/gate parity
