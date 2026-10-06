# Plan 21 — TaskSpec + OutcomeBrief (Spec B)

**Goal:** tasks as sealed, budgeted units of work. A task lives under
`<root>/.apiforge/tasks/<id>/` — `task.yaml`, append-only `revisions/`,
`history.jsonl`, `runs/`. Lifecycle
`draft -> reviewed -> sealed -> ready -> running -> awaiting_supervision ->
accepted`; `rejected|parked|blocked|expired` are refusal/terminal states.
`task seal` binds an Ed25519 signature (reusing `report/keys.py`) to the
exact revision — any amendment writes a new unsealed revision, so a stale
seal can never ride along. The executor never holds the key; `task accept`
requires `accepted_by != executed_by` and at least one `--evidence`.
`task run` executes the recipe (`rules/recipes.yaml`, package data) through
the same `dispatch_step` unit as playbooks, inside `budgets`
(max_rounds/max_calls/deadline) with a no-progress breaker. `brief show`
renders the OutcomeBrief; `DONE` is refused while gaps, missing acceptance,
or open items remain.

- [x] T1: `taskspec/store.py` + `machine.py` — persistence + closed state
  machine; revision snapshots bound by sha256
- [x] T2: `taskspec/service.py` — create/review/seal/ready; sealed
  amendment produces a new unsealed revision
- [x] T3: `taskspec/runner.py` — budgets, no-progress breaker, run record
  per round, acceptance/reject/park/expire, `task status`
- [x] T4: `dispatch_step(verb, ctx)` extracted in `dispatch/runner.py`;
  task inputs may bind `case=` to a real case dir for `evidence emit`
- [x] T5: `brief/render.py` — OutcomeBrief with DONE-refusal conditions;
  `task`/`brief` CLI groups
- [x] T6: `tests/taskspec/test_lifecycle.py` — 13 tests; docs + code table
