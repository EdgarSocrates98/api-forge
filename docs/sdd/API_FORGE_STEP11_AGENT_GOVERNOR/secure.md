---
sdd: 1
feature: API_FORGE_STEP11_AGENT_GOVERNOR
phase: secure
profile: critical
status: done
threat_model:
  - silent risk downgrade — profile selection is max(declared, risk floor);
    an irreversible task cannot land on a cheap profile without the floor
    raising it and naming the clamp
  - unbounded spend — budget_remaining clamps max_agents/max_tokens/max_cost
    ceilings deterministically with the clamp recorded
  - failure-class smuggling — recovery refuses undeclared classes instead of
    guessing a ladder step
  - hidden loop burn — repeated strategy fingerprints inside the window are
    blocked AF-GOV-LOOP-DETECTED before another identical plan spends
  - unresolved laundering — absent signals are named in unresolved; the gain
    mean never fabricates them as zero, and an empty signal set stops closed
  - side-effect smuggling — primitives are pure functions; no primitive
    spawns, mutates ledgers or calls providers
upstream:
  path: verify.md
  sha256: "3eafbfda0a89a7441a1632096d67ed0223bb95e7d986c985e86a01f2c3303f5d"
---

# secure
