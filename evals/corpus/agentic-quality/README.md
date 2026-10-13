# Agentic quality corpus

Recorded specialist outputs (`default_verdict` for every capability plus
per-capability `responses`) and a ground truth per case. `apiforge evals
agentic-quality` replays them through the runtime under each profile and
scores the primary specialist's `verdict`. Claim scope:
`recorded-agentic-outputs` — pass `--responses-dir` with `<case_id>.json`
files to grade real recorded outputs instead of these fixtures.
