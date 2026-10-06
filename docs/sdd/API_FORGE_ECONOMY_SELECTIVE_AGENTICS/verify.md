---
sdd: 1
feature: API_FORGE_ECONOMY_SELECTIVE_AGENTICS
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "0b7c95b8b7a809ab7d88a1bfc0320cc7920414891192377328023af5777351a6"
results:
- gate: targeted tests
  outcome: pass
  evidence: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-tests.txt
- gate: selective eval
  outcome: pass
  evidence: sdd/API_FORGE_ECONOMY_SELECTIVE_AGENTICS/evidence/selective-eval.json
- gate: Ruff
  outcome: pass
  evidence: ruff check + format on touched files
- gate: mypy
  outcome: pass
  evidence: 'Success: no issues found in 402 source files'
- gate: pytest full suite
  outcome: deferred
  evidence: runs once after the last wave, before push
---
# verify

13 corpus cases. Expertise: exact pack sets on 8 intents, 0 packs without trigger, 6–15 KB loaded of a 218 KB catalog. Roles: 40–44% of naive replication, subordinate roles ≤ primary. Referee packet: 34–35% of naive with every evidence id kept. Shadow: 4.9%/10.1%/20.5% sampled for 5%/10%/20% shares over 10000 ids. Audit: 52 agents, 8 keep, 44 merge candidates on declared data.
