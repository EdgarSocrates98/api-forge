---
sdd: 1
feature: API_FORGE_AWS_MESSAGING_SPECIALIZATION_3
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "2f025642cb44a61d8fe4017a7efdde11b691fb9f2182c1a5bfb0d4c900928591"
tasks:
  - id: messaging-contract
    covers: [MessagingAccessIR/v1]
    test: sdd/API_FORGE_AWS_MESSAGING_SPECIALIZATION_3/evidence/messaging-tests.txt
    risk: low
    rollback: remover IR
  - id: messaging-scanner
    covers: [messaging-ir, reliability-signals]
    test: sdd/API_FORGE_AWS_MESSAGING_SPECIALIZATION_3/evidence/messaging-tests.txt
    risk: medium
    rollback: remover adapter
  - id: no-live-message
    covers: [no-message-mutation]
    test: sdd/API_FORGE_AWS_MESSAGING_SPECIALIZATION_3/evidence/messaging-tests.txt
    risk: high
    rollback: manter collectors describe-only
---
# plan

Implementar scanner e comandos `model <service>-access` para os quatro serviços.
