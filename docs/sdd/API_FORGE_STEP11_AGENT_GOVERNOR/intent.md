---
sdd: 1
feature: API_FORGE_STEP11_AGENT_GOVERNOR
phase: intent
profile: critical
status: done
risk_class: high
problem: orchestration had no governor — nothing enforced profile ceilings by
  risk, no signal justified (or refused) an expensive action before spending,
  stopping was implicit, recovery had no declared ladder, and repeated
  strategies could loop silently
success: govern() returns a GovernorDecision whose profile is at least the
  risk floor with every clamp named; expected_gain() scores declared signals
  and refuses when unmeasurable; decide_stop() stops below threshold unless a
  mandatory requirement holds; decide_recovery() walks a closed failure-class
  ladder with caps; check_loop() blocks repeated strategy fingerprints —
  every verb a pure function with explicit unresolved and AF codes
out_of_scope:
  - runtime dispatch consuming decisions (phase 5 control plane wires that)
  - live model calls inside any primitive
  - mutating DecisionRisk/budget contracts already shipped
upstream:
  path: discover.md
  sha256: "4d24d931b572789c6e6f6870024835d14618aaeeedc66bf22ab7e89612fb9dbd"
---

# intent
