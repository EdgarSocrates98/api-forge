# Plan 16 — Debate protocol

**Goal:** when specialists disagree on the same evidence, the disagreement is
a recorded object, never a coin flip. `debate open/submit/close` persists
`debates/<id>.json` inside the case: positions must cite `fact_id` evidence,
closing requires a referee plus submissions on ≥2 sides (quorum), and a
debate that cannot close is recorded `unresolved` — not silently dropped.

- [ ] T1: `debate/service.py` — open (question+sides), submit (position+evidence), close (referee, decision|unresolved, quorum check)
- [ ] T2: `debate` CLI group + `AF-DEBATE-*` codes + tests + docs/gate parity
