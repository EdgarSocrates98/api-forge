---
sdd: 1
feature: API_FORGE_OBSERVABILITY_BOUNDED_PAGINATION_P
phase: discover
profile: standard
status: draft
approaches:
  - id: unbounded-pages
    summary: seguir tokens até o provider terminar
    verdict: refused -- risco de custo e execução interminável
  - id: bounded-pages
    summary: acumular páginas dentro de max_pages e dos budgets
    verdict: chosen -- limite verificável
chosen: bounded-pages
---
# discover

Providers retornam tokens de paginação diferentes e o transport precisava de uma política comum.
