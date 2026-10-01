---
sdd: 1
feature: API_FORGE_AWS_MESSAGING_SPECIALIZATION_3
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "07bcc0ee6c565a3c984f93937988ead8b7f826db27ac815b3ea1cf80dfafb9c3"
covers: [MessagingAccessIR/v1]
api_ir:
  input: Java, Go, Python, TypeScript or configuration source
  output: destinations, roles, operations and reliability signals
---
# contract

`MessagingAccessIR` registra sinais observáveis, mas não afirma exactly-once, ordering ou throughput sem evidência runtime.
