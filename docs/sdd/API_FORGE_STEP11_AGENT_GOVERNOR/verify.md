---
sdd: 1
feature: API_FORGE_STEP11_AGENT_GOVERNOR
phase: verify
profile: critical
status: done
results:
  - focused tests: 46 passed (contracts, governor, gain, stop, recovery, loop, mcp surface)
  - evals agent-governor: 4/4 cases passed (risk floor raise, security clamp, gain/stop, unresolved-gain-stops)
  - CLI smoke: governor decide clamps on irreversible risk + tight budget; governor recover/loop-check work; ghost failure class refuses AF-GOV-FAILURE-CLASS-UNKNOWN
  - Ruff check and format over new/changed files: clean
  - mypy strict over governance + cli + evals: no issues
upstream:
  path: build.md
  sha256: "9c4d53f8b73dd4da4e36de60efbe17ce19c55f6c79b018e2c480bdc7b3330a01"
---

# verify
