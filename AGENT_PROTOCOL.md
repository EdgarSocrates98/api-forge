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

11. **Change-control is a separate governed path.** An `af-change-bundle/1`
    is untrusted input. `change-control collect` may read GitHub only through
    the GET-only adapter and an injected host credential; it never merges,
    pushes, dispatches, deploys, comments, changes status or autofixes.
    `change-control run` consumes the bundle offline and preserves provider
    freshness, deployment safety and permissions as evidence limits unless an
    independent receipt proves them. The repository workflow may open a PR
    only in its separate green-validation job with an explicitly authorized
    least-privilege token; this does not authorize agents or the core to push,
    merge or mutate GitHub.

12. **Every refusal is actionable.** Public error payloads carry an `AF-*`
    code, the rejected `field` and an `unlock` describing the safe next step.
    The code must exist in `docs/catalog-contract.md`; never replace a named
    refusal with a traceback or a generic success value.

## Phase loop

```
next-step → collect → extract facts → judge → hypothesis → experiment
   → measure → verify evidence → update case → next-step
```

One primary variable per experiment. Without a baseline there is no impact
to prove.

For an API change tied to Git/CI/CD, the canonical deterministic route is:

```text
af-change-bundle/1
  → analyze → next-step → graph → evidence → brief
  → verify → publish (JUnit/Markdown) → IDE/UI projection
```

The provider collection is an optional read-only ingress before the bundle is
replayed; it is not part of the offline core.

## Boundaries that are data, not prose

- AWS collection is restricted to the AWS collector family; boto3 lives in
  `apiforge.collectors` and the release gate enforces it. This does not make
  GitHub collection implicit: `change-control collect` is a distinct,
  provider-scoped GET-only adapter and requires its own host credential.
- tree-sitter lives in `adapters/spring|go`; it never executes code and
  never calls a toolchain.
- The core imports no model SDK — `openai|anthropic|litellm` are banned
  from `src/` by the gate; `boto3` is banned outside `collectors/`.
- Every refusal names an `AF-*` code, a `field` and an `unlock`; change-control
  codes are documented in `docs/catalog-contract.md`, while SDD and policy
  refusals remain documented in their respective contracts.

## Agent recommendation contract

Agents understand the need before proposing action. A recommendation keeps
observations, assumptions, alternatives, trade-offs, risks, unresolved gaps,
evidence references, verifier and bounded confidence separate. Agents may
recommend merge strategy, compatibility policy, CI gates or architecture, but
they do not authorize a mutation. The supervisor decides from contracts,
evidence and policy; a human remains responsible for external approval.
