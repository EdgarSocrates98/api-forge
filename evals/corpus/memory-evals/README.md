# memory-evals corpus

§24 deterministic cases over the governed memory store. Each case runs
on an isolated root: `setup.records` are seeded through
`persist_candidate` (the only honest ingress), `action` drives
`query`/`persist_candidate`/`invalidate_suggest`/`quarantine_list`, and
`expect` is checked against the observed contract fields — memory ids
are deterministic (`memory:000000000000000N` in setup order).
