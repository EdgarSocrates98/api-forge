# trace-grading corpus

§23 deterministic cases: each file declares spans (built through
`build_span`, ids/hashes derived) plus an `expect` block checked against
`TraceGrade` under `rules/trace_rubric.yaml`. Use `parent: <index>` to
link a span to an earlier span.
