---
sdd: 1
feature: API_FORGE_AWS_MESSAGING_SPECIALIZATION_3
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "4010af5dc1510805638e13cf63e52cb8da5dd8cfd8f4e926a4372acdfebd97a9"
results:
  - gate: pytest tests/adapters/test_messaging.py -q
    outcome: pass
    evidence: 1 passed
  - gate: ruff, mypy and release gate
    outcome: pass
    evidence: evidence/messaging-tests.txt
---
# verify

Destinos, roles e sinais de confiabilidade são extraídos sem publicar mensagens.
