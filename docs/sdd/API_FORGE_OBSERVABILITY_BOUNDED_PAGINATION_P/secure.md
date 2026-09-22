---
sdd: 1
feature: API_FORGE_OBSERVABILITY_BOUNDED_PAGINATION_P
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "f73d58f27b28a335077a5bd5d37198b44e8318a19552b7e448fa4ad2ac13f446"
threat_model: docs/security/threat-model-mvp.md
---
# secure

O limite cumulativo reduz exaustão de memória, custo de provider e loops de paginação malformados.
