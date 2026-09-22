---
sdd: 1
feature: API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2
phase: discover
profile: standard
status: draft
approaches:
  - id: broker-connect
    summary: conectar no Kafka para descobrir tópicos e consumer groups
    verdict: refused -- exige rede, credenciais e pode alterar offsets
  - id: source-ir-msk-posture
    summary: extrair sinais do código e usar dump MSK de describe
    verdict: chosen -- mantém fronteira offline
chosen: source-ir-msk-posture
---
# discover

MSK já possuía collector de cluster, mas faltava especialização de producer/consumer e um IR de streaming.
