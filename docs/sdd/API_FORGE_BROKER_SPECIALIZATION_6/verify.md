---
sdd: 1
feature: API_FORGE_BROKER_SPECIALIZATION_6
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "1167b851d1223c68c505defa6c6d7b7676b3ffc8bc70f7dafd4edfe743392f57"
results:
  - gate: pytest streaming broker tests -q
    outcome: pass
    evidence: 3 passed
  - gate: ruff, mypy and release gate
    outcome: pass
    evidence: evidence/broker-tests.txt
---
# verify

Os três brokers compartilham IR e não executam consumo.
