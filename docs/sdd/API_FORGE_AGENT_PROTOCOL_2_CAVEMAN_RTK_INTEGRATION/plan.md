---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: plan
profile: standard
status: done
upstream:
  path: architecture.md
  sha256: "4b984ea7a1dc38b512e417bfe42a7245c9ef3b13ad6f479308a73a93842ff611"
tasks:
  - id: compactor
    covers: [compact-output-contract, critical-evidence-preserved, caveman-mode-vocabulary]
    test: sdd/API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION/evidence/compact-tests.txt
    risk: medium
    rollback: disable via mode off
  - id: cli
    covers: [cli-offline-compact]
    test: sdd/API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION/evidence/compact-cli.txt
    risk: low
    rollback: remove command registration
  - id: evals
    covers: [economy-measurable]
    test: sdd/API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION/evidence/economy.txt
    risk: medium
    rollback: retain byte ledger only
---

# plan

O primeiro slice implementa compactação e prova local. A próxima etapa adiciona
filtros por ferramenta, integração com o ledger, workflows de investigação e
evals de equivalência entre saída completa e compactada.
