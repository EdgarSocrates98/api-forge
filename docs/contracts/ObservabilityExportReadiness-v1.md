# ObservabilityExportReadiness/v1

Read-only preflight for a host-owned authenticated export to OTel, Datadog or
Dynatrace. It never resolves secret values and never calls a network endpoint.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `provider` | `otel\|datadog\|dynatrace` | yes |
| `status` | `ready\|review\|blocked` | yes |
| `checks` | array | no |
| `blockers` | array | no |
| `network_called` | boolean | no |

`review` means only human approval or host wiring is missing. Security and
credential mismatches remain `blocked`.
