# Plan 20 — provider tokens and cost

**Goal:** close `tokens_unresolved`. `economy report --transcript <jsonl>`
reads a host transcript (one JSON per line; lines carrying
`message.usage` are summed per `message.model`; others are skipped and
counted) and reports real per-model tokens. `--estimate` adds a chars/4
heuristic over `payload_bytes` — labeled `estimated_tokens` with the method
named, never presented as counted. Cost in dollars requires
`--cost-basis <yaml>` (`model: {input_per_mtok, output_per_mtok}`); models
absent from the basis are named in `cost_basis_missing`, never priced by
guess.

- [ ] T1: `economy/tokens.py` — transcript reader, estimate, cost
- [ ] T2: `economy report` flags + tests + docs/gate parity
