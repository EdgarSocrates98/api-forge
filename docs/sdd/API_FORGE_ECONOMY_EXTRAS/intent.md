---
sdd: 1
feature: API_FORGE_ECONOMY_EXTRAS
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "9e327cd96825aa37495717bc669c68dd01972053de5d430bee84dbacb649c8e3"
problem: 'Verification, retrieval, evidence access, provider choice and prompt shape still defaulted to
  everything: full suites, whole packs, whole chains, strongest model, unstable prompts.'
success:
- verification-plan
- retrieval
- evidence-refs
- economy-doctor
- provider-tiers
- stable-prefix
- locality
- extras-eval
out_of_scope:
- executing-tests
- embeddings
- running-local-models
- provider-cache-headers
owner: api-forge-economy
risk_class: low
risk_signals:
- path:src/apiforge/verification/selection.py
- path:src/apiforge/runtime/role_context.py
---
# intent

Default to the smallest sufficient thing everywhere the earlier waves did not reach, and say why whenever more is needed.
