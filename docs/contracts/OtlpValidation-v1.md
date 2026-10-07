# OtlpValidation/v1

§52 deterministic structural acceptance of an OTLP/JSON payload — the
offline half of collector validation, no network required.

| Field | Meaning |
|---|---|
| `accepted` | `true` only when zero problems |
| `span_count` | Spans inspected |
| `problems` | Every defect named (`traceId` not 32-hex, missing `gen_ai.operation.name`, bad `status.code`, …) |
| `operations` | Distinct `gen_ai.operation.name` values observed |
