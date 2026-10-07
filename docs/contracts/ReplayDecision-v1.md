# ReplayDecision/v1

One §83–§87 control-plane decision re-derived by `apiforge evals replay`
under the current policy and compared to what the run persisted. Decisions
are emitted in the §87 chain order per run:
`loop → model_route_shadow → tool_authorization → trust_admission →
recovery`.

| Field | Meaning |
|---|---|
| `name` | The replayed decision (`loop`, `model_route_shadow`, `tool_authorization`, `trust_admission`, `recovery`) |
| `status` | `same` (stored verdict reproduces), `changed` (policy/data drift flips it), `unresolved` (inputs not persisted — never guessed), `absent` (run never produced it) |
| `stored` / `observed` | Compact stored vs recomputed outcome strings |
| `code` | `AF-REPLAY-DECISION-CHANGED` when status is `changed` |
| `policy_hash` | `sha256:` of the rules file the decision was re-derived under (§86) |
| `detail` | Drift description, missing-input reason, or refusal detail |
