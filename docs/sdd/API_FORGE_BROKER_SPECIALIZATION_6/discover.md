---
sdd: 1
feature: API_FORGE_BROKER_SPECIALIZATION_6
phase: discover
profile: standard
status: draft
approaches:
  - id: broker-specific-runtimes
    summary: iniciar consumidores de RabbitMQ, NATS e Pulsar durante análise
    verdict: refused -- rede e efeitos de consumo
  - id: streaming-ir-extension
    summary: ampliar IR de streaming com brokers declarados
    verdict: chosen -- portátil e offline
chosen: streaming-ir-extension
---
# discover

Kafka/MSK já tinha IR; faltava cobrir brokers populares fora da AWS.
