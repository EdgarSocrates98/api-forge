---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "2eca1a50f6dfa584a588b1ad2c2fe5c84589f93fb9da9d4cde44eb3c90ba800c"
tasks:
  - id: payloads
    covers: [otel-payload, datadog-payload, dynatrace-payload]
    test: sdd/API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S/evidence/exporter-tests.txt
    risk: medium
    rollback: remover build_export_payload
  - id: optional-send
    covers: [disabled-by-default]
    test: sdd/API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S/evidence/exporter-tests.txt
    risk: high
    rollback: bloquear todos os senders
---
# plan

Adicionar builders específicos e callback opcional com receipts de status.
