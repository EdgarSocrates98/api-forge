---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T
phase: benchmark
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "db703aa9f82cc0eac0c0f5908f513defddd8e92bd90051632271dc0be4d5e56a"
baseline: optional payload exporter without auth binding
results:
  - artifact: sdd/API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T/evidence/host-export-tests.txt
    outcome: measured-by-test
    note: latência de envio depende do host e ambiente aprovado
---
# benchmark

Gates locais não executam rede; o sender host-owned define o custo real de exportação.
