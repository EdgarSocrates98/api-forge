---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_ADAPTERS_G
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "66169a2a70b34cf032dbd474ab9d494a51a4ba386661cc2d74505a8a5dac7fd1"
covers: [ReadQuery/v1, ReadPlan/v1]
api_ir:
  input: provider, service, interval and signal set
  output: GET-only plan with limitations and network proof
---
# contract

Providers suportados: OTel, Datadog, Dynatrace e CloudWatch.
