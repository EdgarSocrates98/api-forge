# Observability and external integrations

Language: [English](OBSERVABILITY_INTEGRATIONS.en.md) · [Português (Brasil)](OBSERVABILITY_INTEGRATIONS.md)

API Forge separates the deterministic core from the host that controls
network access, credentials and SDKs.

## Safe flow

```text
ReadPlan / CircuitMetrics
        |
        v
provider query + safety budgets + circuit breaker
        |
        v
HostExportBinding
  compatible provider/backend
  allowlisted HTTPS endpoint
  CredentialStatus available
  enabled=true
  approval_id required
        |
        v
authenticated host callback
        |
        v
receipt sent/failed with evidence
```

Without a valid binding the result is `blocked` or `disabled` and
`network_called=false`. API Forge never resolves secrets, creates
authentication headers, installs an SDK or opens a socket in the core.

## Current backends

- OTel: OTLP-like payload prepared by the builder and ready for a host exporter.
- Datadog: metric series with provider and state tags.
- Dynatrace: gauges with provider and state dimensions.
- CloudWatch: planned/normalized reads; export is a future evolution.

## Real activation still required

1. Implement host-owned callbacks using the official HTTP/SDK with host-side
   timeout and retry.
2. Resolve credentials only through the host broker and redact headers/logs.
3. Configure environment-specific endpoints and allowlists without placeholders.
4. Execute in an approved account/tenant with evidence and rollback.
5. Validate semantic conventions, rate limits, retention and per-backend cost.

See the complete map in [API_FORGE_EVOLUTION_MAP.en.md](API_FORGE_EVOLUTION_MAP.en.md).
