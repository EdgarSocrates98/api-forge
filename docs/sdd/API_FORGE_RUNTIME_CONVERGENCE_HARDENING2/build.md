---
sdd: 1
feature: API_FORGE_RUNTIME_CONVERGENCE_HARDENING2
phase: build
profile: critical
status: draft
tasks:
  - id: p0-truthfulness
    status: done
  - id: p0-loop
    status: done
  - id: p0-recovery
    status: done
  - id: p0-retrieval
    status: done
  - id: p1-routing
    status: pending
  - id: p1-authority
    status: pending
  - id: p1-memory
    status: pending
  - id: p1-lab-mcp
    status: pending
  - id: release-evidence
    status: pending
claims:
  - implementation is not accepted until its focused proof and independent verification are recorded
  - p0-truthfulness proof records unresolved/partial token state and model-call correlation
  - p0-loop proof records real trajectory history and blocks repeated strategy before invocation
  - p0-recovery proof records failure classification and recovery decision before each retry
  - p0-retrieval proof records one effective score basis for ranking and sufficiency plus graph depth provenance
upstream:
  path: plan.md
  sha256: "1c06b43e224fec46de6f9db25e2102a9e561a62e6863c04f9f0e22ed245fe3d4"
---

# build

Implementation is executed in atomic tasks. Each task must pass its focused
proof before its commit is created.
