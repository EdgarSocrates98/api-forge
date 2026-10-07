# ShadowRecord/v1

§29 parallel-run observation. In `shadow` mode the candidate executes in
parallel but **never governs** — the legacy decision rules; the candidate's
answer is recorded for comparison.

| Field | Meaning |
|---|---|
| `candidate_decision` / `legacy_decision` | Both serialized decision payloads |
| `difference` | Sorted top-level field paths where they differ |
| `confidence` | Declared confidence of the evaluation (`0..1`), or `null` |
| `evidence_refs` | Evidence backing the observation |

Records are append-only in `control-plane/shadow.jsonl`; they are the
promotion evidence trail.
