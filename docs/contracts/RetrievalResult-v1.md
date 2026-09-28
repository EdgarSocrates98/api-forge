# RetrievalResult/v1

`RetrievalResult/v1` is `apiforge knowledge search --query Q [--tier 1|2|3]`.

| Field | Meaning |
|---|---|
| `expanded_terms` / `added_terms` | Query words plus terms added by `rules/query_expansion.yaml` (no model involved) |
| `tier` / `next_tier` | 1 = top 3, 2 = top 5, 3 = up to 20; `next_tier` is set when more candidates exist |
| `passages[]` | `{pack_id, file, heading, score, signals{heading_hits, body_hits, selected_pack}, ref, bytes}`; `ref` is the ctx:// of the passage |
| `candidates` | Passages that matched at least one term |
| `unresolved` | `no-passage-matched` when nothing matched |
