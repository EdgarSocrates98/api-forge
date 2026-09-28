# LiveEvidenceDecision/v1

`LiveEvidenceDecision/v1` is `apiforge evidence gate --question <text>` (§97). Terms come from `rules/live_evidence_triggers.yaml`.

| Field | Meaning |
|---|---|
| `question_class` | `static`, `runtime` or `ambiguous` |
| `mode` | `static`, `fixture` (runtime question with `--offline`) or `live_read_only`; `live_mutation` is refused with `AF-EVIDENCE-MUTATION-REFUSED` |
| `live_allowed` | `true` only for runtime questions in an online run |
| `runtime_terms` / `static_terms` | Declared terms found in the question |
| `suggested_sources` | Read-only sources for runtime questions (otel, datadog, dynatrace, cloudwatch, x-ray) |
| `requires_receipt` | Runtime evidence must bring a read-only receipt |
| `escalate_if_unanswered` | Ambiguous question: local first, then ask again with the runtime effect named |
| `reasons` | Why the mode was chosen |
