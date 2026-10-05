# knowledge-drift corpus

§29 deterministic cases: each file materializes a synthetic pack
(pack.yaml + source_authority) and `SourceObservation` receipts, then
checks the `KnowledgeDrift` rollup — `verified`, `stale`, `conflicted`,
`deprecated` and `unresolved` states through `detect_pack_drift`.
