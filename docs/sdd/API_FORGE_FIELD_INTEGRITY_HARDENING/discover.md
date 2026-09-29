---
sdd: 1
feature: API_FORGE_FIELD_INTEGRITY_HARDENING
phase: discover
profile: critical
status: draft
approaches:
- id: lock-plus-receipt
  summary: sealed cycle.lock.json identity plus verification receipt bound to an annotation digest
  verdict: chosen by the owner -- mirrors BenchmarkIdentity/v1, minimal diff
- id: inline-corpus-hashes
  summary: identity block written inside corpus.yaml
  verdict: refused -- self-referential hash, mixes declaration with seal
- id: event-ledger
  summary: append-only field event ledger replayed by the report
  verdict: refused -- rewrites storage, beyond a pre-cycle hardening
chosen: lock-plus-receipt
---
# discover

Source: `prompt_evo_ajuste.md`, an external review of `main@9ca39f9`. Every finding was confirmed in code before scoping; the unenforced `max_runs`/`max_weeks` gate was found in addition. Brainstorm: `.claude/sdd/features/BRAINSTORM_FIELD_INTEGRITY_HARDENING.md`.
