---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CREDENTIAL_BROKER_J
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "bfc79a39b850f638a00f6996799e46d26b3624f24ab966fb7c34437a9fdb1106"
problem: >
  Conectores reais não devem receber secrets no núcleo nem tratar ausência de
  broker como sucesso de observabilidade.
success: [metadata-only-reference, blocked-without-broker, no-secret-output]
out_of_scope: [secret-store-access, live-http-client, mutation]
owner: api-forge-security
---
# intent

Formalizar o broker e o gate de leitura.
