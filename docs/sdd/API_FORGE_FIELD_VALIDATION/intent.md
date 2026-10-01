---
sdd: 1
feature: API_FORGE_FIELD_VALIDATION
phase: intent
profile: critical
status: draft
upstream:
  path: discover.md
  sha256: "e1f67173c4c783b3342e52c8fd669ceb7d2abaf4a5f703b304ce30b584b64d64"
problem: 'The roadmap is chosen by intuition: evals are synthetic, no real-repository run is recorded,
  and the workspace graph only holds declared cross-repo relations.'
success:
- pre-registered-corpus
- evidence-joined-record
- closed-enum-annotation
- blind-verification
- deterministic-gap-report
- isolated-inference
- anonymized-export
out_of_scope:
- arazzo-overlay-openapi-3-2-parsing
- contract-to-runtime-intelligence
- framework-packs
- grpc-stub-inference
- running-the-field-cycle
owner: api-forge-field
risk_class: high
risk_signals:
- keyword:cross-repo
- path:src/apiforge/workspace/graph.py
- path:src/apiforge/contracts/workspace.py
- path:src/apiforge/mcp/tools.py
---
# intent

Measure where and why users leave the API Forge flow on real repositories, and let the inference bet prove itself only by A/B.
