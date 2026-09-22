---
sdd: 1
feature: API_FORGE_LOW_LATENCY_DATA_SPECIALIZATION_4
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "c50647901b4389d077be338c6bf48a1830321cba65e4c8623365947edcfc3ad2"
files: [src/apiforge/data_governance.py, src/apiforge/contracts/stubs.py]
decisions:
  - id: facts-first
    decision: compor o perfil sobre facts existentes, sem reanalisar valores
    rollback: remover build_data_performance_profile
  - id: no-prescription
    decision: reportar risco, não sugerir índice, TTL ou capacidade automaticamente
    rollback: manter somente facts brutos
---
# architecture

O perfil é uma camada de interpretação conservadora sobre os scanners atuais.
