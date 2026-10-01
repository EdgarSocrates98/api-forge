---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "5e4bbc59c38ad96d5a5ad87fbabba51af3a774eade57d1a14e57bace7fdbbac1"
threat_model: docs/security/threat-model-mvp.md
---
# secure

- O core nunca importa `boto3`; o collector usa import tardio e cliente injetável.
- `collect neptune-explain` só chama operações de `ALLOWED_OPERATIONS` (frozenset testado);
  toda recusa ocorre antes de criar o cliente (teste com cliente que falha ao ser tocado).
- Planos que executam a query (`--profile`) exigem texto literal sem mutação e
  `--reader-endpoint` igual a `--endpoint`; o recibo registra `reader_declared`, nunca
  `reader_verified`.
- Explain de mutação é recusado (`AF-GDB-PROFILE-MUTATION`); SPARQL só via dump.
- Recibos guardam `query_sha256`; dumps reais podem conter literais — redigir antes de versionar.
- `AF-GDB-008` aponta texto de query montado dinamicamente (injeção); exploração fica com
  `api-security-reviewer`.
