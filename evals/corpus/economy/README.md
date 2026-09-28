# Economy corpus

Twelve cases that measure `apiforge context capsule` against today's agent
path. Each case copies `fixture` into `<tmp>/<id>/proj`, the contract into
`<tmp>/<id>/openapi.yaml`, runs `analyze`, then compares:

- **baseline** — `context resolve` payload plus every file named by
  `required_refs`, read whole (recorded once in `baseline.json`);
- **capsule** — the emitted capsule plus a full expansion of every ref it
  carries (conservative bound).

Gates: `evidence_recall(capsule) >= evidence_recall(baseline)` in every case,
median byte reduction `>= --min-reduction` (default 0.40), byte-identical
capsules across two builds. Tokens stay `unresolved` — bytes are not tokens.

```text
apiforge evals economy --record-baseline   # only when fixtures change
apiforge evals economy                     # exit 1 when a gate fails
```

`required_refs[*]` match a capsule ref when `source == path`, `kind` matches
(if given) and `symbol` appears in the stored object.
