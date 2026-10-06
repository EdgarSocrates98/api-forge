---
sdd: 1
feature: API_FORGE_EVOLUTION1_GOVERNED_BUDGETS
phase: secure
profile: critical
status: done
upstream:
  path: verify.md
  sha256: "ac3b7c32aef69663d3a57b7138f86e0122c3ebc694e2bef9baa6bbf6ddc1254f"
threat_model:
  - rejected spends never enter the append-only journal
  - token limits fail closed when measurement is absent
  - plan ids cannot be silently reused with a different content hash
  - no provider, model, cloud or external mutation is reachable
---

# secure

The budget plane is local-only, closed-contract validated and fail-closed for
missing token measurements. It cannot authorize external mutation, overwrite a
plan, or infer provider cost. Corrupt rows refuse with an actionable code.
