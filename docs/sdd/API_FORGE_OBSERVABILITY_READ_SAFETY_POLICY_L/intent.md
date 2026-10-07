---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_SAFETY_POLICY_L
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "4bd8bf824f996ef233c3ae257b35042e323a4009903abb65b0cdeb4e594f453b"
problem: >
  Um provider pode devolver cardinalidade ou payload acima do orçamento esperado,
  causando pressão de memória, custo e ruído no agente.
success: [bounded-records, bounded-bytes, explicit-blocked-receipt]
out_of_scope: [pagination, provider-rate-limit, live-sdk]
owner: api-forge-observability
---
# intent

Rejeitar respostas acima de limites determinísticos sem permitir mutações.
