---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: ship
profile: standard
status: draft
upstream:
  path: benchmark.md
  sha256: "8cb0719ff2ca591f404211ac0aa4ba9b6a52200d438c2c4209c1a755cc3b206a"
deviations:
  - "Native adapters implemented; vendor installation and external RTK binary remain out of scope."
evidence:
  - path: sdd/API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION/evidence/compact-tests.txt
    sha256: "f7710f7539d4ed7736cfb9b70cd8599f26714c3a16467a28e423c27a4e45b8a6"
  - path: sdd/API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION/evidence/compact-cli.txt
    sha256: "a80c13157fdd2201ff44e1ba4dbfa63e13e8954a71bf8693de57aad7b4364bc1"
---

# ship

Entrega inicial pronta para revisão. O próximo ship deve incluir filtros por
ferramenta, integração explícita com o ledger e evals de não perda semântica.
