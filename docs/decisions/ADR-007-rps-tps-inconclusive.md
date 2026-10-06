# ADR-007: RPS and TPS are distinct; inconclusive is a verdict

## Status

Accepted — 2026-09-26.

## Context

Load tools report request counts; the prompt defines TPS as *completed
business transactions*. Conflating them inflates success — a run can serve
1k rps while completing zero transactions. Equally, a run without baseline,
with a saturated generator, or with unobserved downstreams cannot be called
"passed"; calling it "failed" is also wrong — it simply did not answer.

## Decision

`PerformanceRun` carries `rps_received`/`rps_processed` separately from
`target_tps`/`achieved_tps`/`successful_tps`/`failed_tps`, and
`tps_completed_transactions` is a boolean claim that is only valid when the
source proves TPS counted completed transactions. `perf/verdict.py` emits
`passed | failed | inconclusive`: every missing precondition is a named
inconclusive condition (no baseline, generator dropped iterations, target
not reached, downstreams unobserved, TPS not proven, SLO absent). Optional
fields stay `None` — absent measurement is never zero.

## Consequences

- A report can never "pass by absence of error": the verdict requires
  affirmative evidence of validity conditions.
- Load-report readers (k6, locust, jmeter, gatling, vegeta, wrk, hey) keep
  RPS and TPS as separate measures; pytest-benchmark is never read as a
  load run.
- Generator saturation is itself evidence — `dropped_iterations` and
  AF-TEST-104 name it instead of silently discarding the run.
