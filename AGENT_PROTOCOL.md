# Agent protocol — API Forge

Every agent and every skill **points at** this file; none embeds it.
**Read it**: the rules below do not reach your context by themselves.

These rules are hard: they are what makes the result identical under any
model and any tool.

## Rules

1. **Open or load the case before any analysis.** Investigation without a
   persisted case (`.apiforge/case/`) is not resumable in another tool, and
   resumability is a requirement, not a convenience.
2. **Call `next-step` before choosing a route.** The decision tree lives in
   `rules/catalog/routing.yaml` — it is data, not judgment. Picking a
   coordinator by inspection is exactly what diverges between models.
3. **No number in output without a `fact_id` behind it.** Every quantitative
   claim cites `rule_id` and the `fact_id` of the evidence. Without a Fact
   it is a hypothesis, and it must be labeled a hypothesis.
4. **Use `rules lookup` instead of memory** for thresholds, guidance and
   sources. You do not need to know the knowledge; you need to query it.
   `apiforge rules list [--area]` is the index; `apiforge rules lookup
   <id>` is the full rule. Do not `Read` `rules/catalog/*.yaml` — same
   answer by the expensive path.
5. **Generated code travels through the sandbox, never the main tree.**
   `build endpoint` emits a diff and proves it in the copy sandbox;
   promotion happens only via `--into-worktree` with `--approve` recorded
   as approval evidence. There is no "just write the file" path.
6. **Record in the case** each verb used, the result, and why discarded
   options were skipped. As a coordinator, record **which executor ran** —
   `af-inventory`, `af-extractor`, `af-judge`, `af-verifier` or
   `af-synthesizer` — **and with what result**.
7. **Always report `unresolved`.** An unresolved diagnostic is a blind
   spot, not an absence of problems. Never omit the count; never let
   `confirmed` stand on extraction uncertainty.
8. **Confirm the framework before citing API shape.** `--framework`
   detection counts files; `auto` is a heuristic, not evidence. State the
   detected framework; divergence between contract and code is judged, not
   papered over.
9. **Destructive operations you do not run** — you recommend, and the
   decision goes up to whoever can be asked. Worktree promotion requires
   recorded approval; anything past that boundary is a named refusal, not
   a workaround.
10. **A receipt proves correspondence, never authorship.** `evidence verify`
    re-hashes artifacts and reports divergence; it says *these are the same
    bytes*, not *who wrote them*. Gates are satisfied by evidence kinds —
    presence of the named kind, never the content, and never a boolean.

## Phase loop

```
next-step → collect → extract facts → judge → hypothesis → experiment
   → measure → verify evidence → update case → next-step
```

One primary variable per experiment. Without a baseline there is no impact
to prove.

## Boundaries that are data, not prose

- `collect *` is the only verb family that touches AWS; boto3 lives in
  `apiforge.collectors` and the release gate enforces it.
- tree-sitter lives in `adapters/spring|go`; it never executes code and
  never calls a toolchain.
- The core imports no model SDK — `openai|anthropic|litellm` are banned
  from `src/` by the gate; `boto3` is banned outside `collectors/`.
- Every refusal names an `AF-*` code, a `field` and an `unlock` — documented
  in `docs/catalog-contract.md`, `docs/sdd-contract.md` and
  `docs/policy-contract.md`.
