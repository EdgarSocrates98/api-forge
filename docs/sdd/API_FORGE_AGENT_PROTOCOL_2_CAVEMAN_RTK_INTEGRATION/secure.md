---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: secure
profile: standard
status: done
upstream:
  path: verify.md
  sha256: "5134ba3127864a1fe4c71a61425ed90148357391d9842d1eaea38a99c26185a0"
threat_model: docs/security/threat-model-mvp.md
---

# secure

O adaptador é somente leitura, não executa comandos, não faz rede e não
promove artefatos. O texto completo permanece disponível para auditoria; o
compactador não é autoridade para `DONE`.
