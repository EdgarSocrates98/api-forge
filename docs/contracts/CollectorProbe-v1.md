# CollectorProbe/v1

§52 the real-collector acceptance record.

| Field | Meaning |
|---|---|
| `endpoint` | OTLP/HTTP URL the payload was POSTed to |
| `sent` / `accepted` | Spans submitted / spans confirmed in the collector's output file |
| `status` | `accepted`, `refused` (HTTP error or missing spans) or `unresolved` (endpoint unreachable, no output declared) |
| `code` | `AF-OTEL-COLLECTOR-*` refusal/unresolved code |
| `unresolved` | Fields that could not be determined |

Acceptance is never claimed on faith: without the collector's declared
output file containing the sent span ids, the probe stays `unresolved` or
`refused`.
