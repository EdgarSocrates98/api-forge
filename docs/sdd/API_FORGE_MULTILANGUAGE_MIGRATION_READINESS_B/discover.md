---
sdd: 1
feature: API_FORGE_MULTILANGUAGE_MIGRATION_READINESS_B
phase: discover
profile: migration
status: draft
approaches:
  - id: version-string-only
    summary: tratar runtime como pares de strings
    verdict: refused -- não prova toolchain nem readiness
  - id: matrix-readiness-gate
    summary: combinar matriz, direção, capacidades e findings
    verdict: chosen -- planeja migração sem adivinhar
chosen: matrix-readiness-gate
---
# discover

Java, Go e Python já tinham matrizes; faltava transformar a descoberta em gate de prontidão.
