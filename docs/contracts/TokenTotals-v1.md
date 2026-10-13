# TokenTotals/v1

Summed usage inside **one** basis bucket. A `TokenTotals` row only ever
aggregates entries of a single basis — observed rows never inflate an
estimated total and vice versa.

| Field | Meaning |
|---|---|
| `input_tokens` … `reasoning_tokens` | Per-field sums over the bucket |
| `entries` | Row count summed |

`total()` returns the sum across all five token fields.
