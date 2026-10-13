---
sdd: 1
feature: API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "2c8ec4709b32923140a9d38f6eca6b25550aae693a120a37bbceb8c05586b497"
results:
  - gate: pytest tests/adapters/test_streaming.py -q
    outcome: pass
    evidence: 2 passed
  - gate: ruff, mypy and release gate
    outcome: pass
    evidence: evidence/kafka-tests.txt
---
# verify

O scanner reconhece tópico, grupo, producer, consumer e sinais de entrega sem tocar offsets.
