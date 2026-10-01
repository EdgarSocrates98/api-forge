---
sdd: 1
feature: API_FORGE_GRAPH_DOCUMENT_SPECIALIZATION_7
phase: discover
profile: standard
status: draft
approaches:
  - id: generic-query-advice
    summary: tratar MongoDB e Neptune como o mesmo banco
    verdict: refused -- document queries e graph traversals têm riscos distintos
  - id: fact-specific-profile
    summary: derivar riscos de unfiltered writes e traversals sem limite
    verdict: chosen -- preserva semântica de cada engine
chosen: fact-specific-profile
---
# discover

MongoDB/DocumentDB e Neptune já tinham scanners, mas seus riscos avançados ainda não chegavam a um perfil comum.
