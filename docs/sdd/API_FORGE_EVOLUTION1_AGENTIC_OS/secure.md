---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENTIC_OS
phase: secure
profile: critical
status: done
upstream:
  path: verify.md
  sha256: "84bc6b8a59ab00bd0aebddb198ddc7316b5cfd353a20c02f930867cacd025b9a"
threat_model:
  - data is not instruction: every external/model entry carries origin and taint
  - memory poisoning: model-generated and external-untrusted promotion is gated
  - stale/wrong-runtime reuse: expiry and environment filters remain visible
  - deletion/audit gap: invalidation is append-only
  - confused deputy: no store imports provider SDKs or performs external mutation
---

# secure

Wave 1 applies deterministic guardrails only. A dedicated security corpus,
tool-risk profiles and allowlist-by-agent are planned for the next wave and
are not silently claimed here.

