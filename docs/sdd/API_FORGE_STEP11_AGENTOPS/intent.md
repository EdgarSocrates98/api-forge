---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: intent
profile: critical
status: done
risk_class: medium
problem: runs leave evidence across five local ledgers but nothing joins
  them; there is no per-run report, no two-run comparison and no detector
  for token waste — §54–§57 unimplemented
success: "apiforge agentops inspect <run> emits the §54 section set plus
  waste and decision path; compare emits the §55 axis set with honest
  verdicts; waste runs the declared detectors in rules/agentops_waste.yaml
  labeling every finding observed/estimated/hypothesis; missing data is
  always unresolved"
out_of_scope:
  - live provider cost lookups (cost stays unresolved without pricing)
  - per-run memory attribution (memory rows carry no run_id)
  - auto-remediation of detected waste
upstream:
  path: discover.md
  sha256: "6c0752b06b14b897b9fb337bc66053ddc1336b448b925b064ec28ba6bd3c9f35"
---

# intent

AgentOps read plane only — it observes and reports; it never mutates runs,
ledgers or policies.
