---
sdd: 1
feature: API_FORGE_DEVIN_INTEGRATION
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "11e2b1946b99c81a5f2f6c0f3322adfe1c684abe32f39d7618cc65cbadbb778c"
files: [src/apiforge/contracts/devin.py, src/apiforge/integrations/devin.py, src/apiforge/cli.py]
decisions:
  - id: no-provider-call
    decision: keep Devin integration payload-only and probe local executable only
    rollback: remove integrations/devin.py and retain host-neutral support
  - id: evidence-boundary
    decision: product docs remain declared; local version probe is observed
    rollback: remove capability declaration projection
---
# architecture

The pure builder projects one contract to Desktop, CLI and Cloud; native
`.devin/` assets provide runtime-specific guardrails.
