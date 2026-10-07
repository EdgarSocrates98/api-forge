---
sdd: 1
feature: API_FORGE_GRAPH_DOCUMENT_SPECIALIZATION_7
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "45c591594723caadfb6485d25247958d88d2dc77e16024bc279333361b1f7e55"
tasks:
  - id: graph-document-profile
    status: done
    evidence: sdd/API_FORGE_GRAPH_DOCUMENT_SPECIALIZATION_7/evidence/graph-document-tests.txt
claims: [mongo-unfiltered-write, neptune-unbounded-traversal, engine-specific]
---
# build

O `DataPerformanceProfile` agora cobre MongoDB/DocumentDB e Neptune.
