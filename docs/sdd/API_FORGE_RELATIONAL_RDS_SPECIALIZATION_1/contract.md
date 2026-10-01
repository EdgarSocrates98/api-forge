---
sdd: 1
feature: API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "d595a43daee0b70d8996aca2f4289d6c9c1008c357993f3dc5daa33a710699a3"
covers: [DataAccessIR/v1, aws.rds.offline-dump]
api_ir:
  input: Python, Java, Go or SQL source plus injected RDS client for collection
  output: facts, DataAccessIR and hashed RDS dump
---
# contract

O scanner registra observações declaradas; não infere índice, plano de execução ou performance real.
