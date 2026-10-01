---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: benchmark
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "20ff763239b3f64d1f0d2e9a29025e918da93c47be8614d7303cb0447de6463a"
baseline: "CompactedOutput original_bytes versus emitted_bytes on local artifacts"
results:
  - artifact: tests/agentops/test_compact.py
    outcome: measured-by-test
    note: "The full economy comparison suite is the next slice."
---

# benchmark

O contrato já emite bytes originais, bytes emitidos, linhas omitidas e SHA-256.
A comparação por comando, modelo e sessão será adicionada após os filtros RTK
específicos e não é inventada nesta entrega.
