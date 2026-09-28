# BenchmarkIdentity/v1

`BenchmarkIdentity/v1` names the experiment an `evals agentic-quality` report
measured. A `--baseline` report counts as a regression check only when its
identity is the same experiment; otherwise it is refused with
`AF-EVALS-BASELINE-MISMATCH` unless `--allow-cross-corpus-baseline` is passed,
in which case the report records `baseline_scope: cross_corpus` and the gates
are suffixed `_cross_corpus`.

| Field | Meaning |
|---|---|
| `corpus_sha256` | sha256 over each case file name and its LF-normalized bytes, in sorted order |
| `case_ids_sha256` | sha256 of the sorted case ids |
| `case_count` | Number of cases |
| `profiles` | Profiles evaluated (`economy`, `balanced`, `deep`) |
| `claim_scope` | What the report may claim (`recorded-agentic-outputs`) |
| `evaluator_version` | Evaluator and apiforge version; reported, not compared |
