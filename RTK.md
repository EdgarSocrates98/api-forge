# API Forge RTK contract

RTK (Reasoning/Transcript Kernel) is the compact context contract for API
Forge. It reduces repeated context without changing the source of truth.

## Source of truth

- `AGENTS.md` and `AGENT_PROTOCOL.md` define operating policy.
- `.apiforge/case/` contains the persisted case and its hashes.
- Generated artifacts, receipts, findings and unresolved diagnostics are
  authoritative; a compact response is only a projection.
- `apiforge context compact` may reduce output, but it must preserve `AF-*`
  codes, `fact_id`s, hashes, failed checks, security findings and unresolved
  state.

## Context order

Load only the smallest complete chain needed for the current decision:

```text
case manifest → api IR → facts → findings → next-step → graph → evidence → brief
```

For API changes tied to Git or CI/CD, add the governed bundle and provider
receipt before replaying it:

```text
af-change-bundle/1 → collect/replay → analyze → verify → publish → surface
```

## Output rules

Every conclusion keeps these fields separate:

- observed facts and their evidence references;
- assumptions and alternatives;
- risks, limitations and `unresolved` items;
- verifier and bounded confidence;
- next action and safe unlock when a refusal occurs.

Never compress a refusal into a success value, infer runtime behavior from a
fixture, or remove an unresolved diagnostic to make a gate green.

## Safe compaction

Use:

```text
apiforge context compact --input <command-output.txt> --command <verb>
apiforge economy report --root .
```

The compact view is invalid if it omits a critical error, evidence hash,
finding status, policy boundary or unresolved diagnostic. External systems
remain read-only unless a dedicated host adapter has an explicit policy,
approval, rollback and receipt.
