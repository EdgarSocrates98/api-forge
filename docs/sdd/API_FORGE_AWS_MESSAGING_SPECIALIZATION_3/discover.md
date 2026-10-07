---
sdd: 1
feature: API_FORGE_AWS_MESSAGING_SPECIALIZATION_3
phase: discover
profile: standard
status: draft
approaches:
  - id: send-live-message
    summary: publicar e consumir mensagens para descobrir o fluxo
    verdict: refused -- mutação externa e risco de duplicidade
  - id: source-and-dump-ir
    summary: extrair destinos, operações e sinais de confiabilidade offline
    verdict: chosen -- seguro e auditável
chosen: source-and-dump-ir
---
# discover

Collectors AWS de SQS, SNS e EventBridge já existiam, mas faltava uma IR de mensageria e Kinesis.
