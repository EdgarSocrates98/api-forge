---
sdd: 1
feature: API_FORGE_ECONOMY_EXTRAS
phase: discover
profile: standard
status: draft
approaches:
- id: seven-deterministic-verbs
  summary: small read-only modules behind verbs for verification, retrieval, evidence, doctor, tiers,
    prompts and locality
  verdict: chosen -- additive, independently testable
- id: fold-into-existing-verbs
  summary: extend context capsule and knowledge select
  verdict: refused -- overloads contracts shipped in earlier waves
chosen: seven-deterministic-verbs
---
# discover

Source: `prompt_evo_economy.md` §45–§49, §55–§58, §60–§63 and §81–§83 — the sections not covered by waves 0–6.
