# ADR-008: tool registry — runnable allowlist vs import-only readers

## Status

Accepted — 2026-09-26.

## Context

The platform needs tools in two roles: executing a scanner locally, and
reading a report an operator produced elsewhere (CI, a load tool the local
runner cannot drive). Mixing them lets a "supported" tool silently mean
"we read its output" while the user expects execution — or worse, lets the
runner shell out to anything.

## Decision

`TOOL_REGISTRY` is the single source: every entry declares category,
license, input/output, capabilities, limits, cost, network/credential
needs, local+AWS support, parser, compatibility, evidence producer and
supported modes; `installed` is measured via `shutil.which`, never
declared. `run tool` only executes the four binaries with closed argv
templates (semgrep, trivy, gitleaks, k6); registry tools that are report
readers refuse with `AF-RUN-IMPORT-ONLY`. Load runs against remote or
unresolvable targets gate on policy `sensitive` + `--approve`
(`AF-RUN-PROD-GATE`). Distributed Load Testing on AWS stays external and
policy-gated — `run` never touches AWS.

## Consequences

- `run list` answers "what exists, what is installed, what it costs,
  what evidence it produces" without executing anything.
- Execution-mode breadth (docker/ECS/scheduled/CI) is declared per tool
  as the tool's own capability; the local executor only ever runs `local`.
- No production load test can run without an approval reference.
