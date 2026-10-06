# Plan 17 — Real dispatch: agent mirrors + deterministic playbook runner

**Goal:** dispatch stops being prose-only. (a) `agents sync` generates the
platform-native mirrors (`.agents/agents/`, `.claude/agents/`) so hosts with
subagent runtimes can actually spawn the coordinators — the gate fails on
drift. (b) `dispatch run --coordinator <name> --case <dir>` executes each
playbook step whose verb is deterministic and whose inputs are in the
dispatch context; every other step is `pending` with the missing input or
the refusal reason named — `collect *` never runs inside dispatch.

- [ ] T1: `dispatch/runner.py` — closed verb table, ctx inputs, per-step output sha256, run record under `case/dispatch/`
- [ ] T2: `dispatch run` verb + `agents sync` + mirror-drift gate check
- [ ] T3: tests + docs/gate parity (AF-DISPATCH-*, AF-AGENT-*)
