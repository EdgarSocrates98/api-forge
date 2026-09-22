---
sdd: 1
feature: API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2
phase: benchmark
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "c9d5d1ef1fa055e1dbefe5ada14e5bd19baf778d82fdd4c6f3d4401c59767bf1"
baseline: static Kafka source extraction tests
results:
  - artifact: sdd/API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2/evidence/kafka-tests.txt
    outcome: measured-by-test
    note: lag e throughput reais requerem adapter aprovado
---
# benchmark

A fase mede sinais declarados, não throughput ou consumer lag real.
