---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: secure
profile: critical
status: done
threat_model:
  - asset: decision and evidence integrity
    threats: forged receipts, stale upstreams, false green metrics
    controls: hashes, fail-closed states, independent verification
  - asset: budget and provider boundary
    threats: uncontrolled retries, hidden live calls, cost escalation
    controls: governance context, budget clamps, adapter policy gates
  - asset: knowledge and memory
    threats: poisoned retrieval, unsupported semantic claims, cross-tenant leakage
    controls: provenance, namespace filters, poisoning quarantine and unresolved evidence
  - asset: delivery pipeline
    threats: dependency drift, unauthorized PR mutation, unreviewed auto-merge
    controls: lock check, least-privilege green-validation job and branch protection
upstream:
  path: verify.md
  sha256: "807bee29feded8a2aecd3b7182f5d8a5683d50a680f882e018e6679a1785c41f"
---

# secure

The secure boundary is local and deterministic. Secret values, credentials,
provider tokens and production data are not collected. Any external freshness
or permission claim stays unresolved until an approved adapter supplies evidence.
