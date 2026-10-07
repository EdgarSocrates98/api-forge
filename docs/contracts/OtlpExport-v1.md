# OtlpExport/v1

§50 envelope for one OTLP `ExportTraceServiceRequest` payload — no OTel SDK
dependency; the exporter emits the canonical JSON shape directly.

| Field | Meaning |
|---|---|
| `service_name` | `service.name` resource attribute (default `apiforge`) |
| `span_count` | Ledger spans converted |
| `payload` | The OTLP/JSON object: `resourceSpans → scopeSpans → spans` |
| `source_sha256` | Hash of the source `agent-spans.jsonl` ledger |
| `unresolved` | Spans with unrepresentable fields (e.g. bad timestamps) |

Each span carries `gen_ai.operation.name`, `gen_ai.agent.name`,
`gen_ai.tool.name` and `apiforge.*` correlation attributes; model/tool/
retrieval calls export as `kind: CLIENT`, the rest `INTERNAL`.
