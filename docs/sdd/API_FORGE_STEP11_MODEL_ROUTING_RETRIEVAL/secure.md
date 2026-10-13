---
sdd: 1
feature: API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL
phase: secure
profile: critical
status: done
threat_model:
  - cheap-model capture — hard constraints plus the quality_floor with
    min_evaluations stop a cheap weak model from winning on cost alone
  - synthetic self-promotion — route promote requires real evaluation
    volume and floor quality; it refuses AF-ROUTE-PROMOTION-EVIDENCE and
    still needs the phase-5 ApprovalGate
  - undeclared model smuggling — candidates come only from the declared
    policy yaml; anything not declared cannot be ranked
  - silent rewrite — QueryRewrite always records original and gate result;
    a blocked rewrite returns null rewritten plus the refusing reason
  - semantic exfiltration — the SemanticAdapter is local-only
    (HashFeatureSimilarityAdapter); no network, no provider SDK, L3 skipped with
    unresolved when undeclared
  - cost fabrication — RetrievalComparison reports cost only from a
    declared rate; without one cost stays null and cost_rate lands in
    unresolved
upstream:
  path: verify.md
  sha256: "d6fbb5957e3ebd4d9c1a96439176569dcedc62ed8ef355c2b5352baeae25ce39"
---

# secure

The routing surface is read-only: ranking, scorecards, ladders and rewrite
gates produce decisions and records — the only mutation path is
`route promote`, which flows through the phase-5 PromotionEvidence and
ApprovalGate machinery rather than mutating any mode itself.
