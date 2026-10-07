---
sdd: 1
feature: API_FORGE_STEP11_CONTEXT_QUALITY
phase: verify
profile: critical
status: done
upstream:
  path: build.md
  sha256: "5a2d91584b796b1514b576112c301ec368f4ae5c688199b6a19b95e19df305e4"
results:
  - focused tests: 74 passed (tests/context + tests/economy/test_selective_agentics.py)
  - evals context-quality: 4/4 cases passed
  - Ruff check and format over src tests: clean (879 files)
  - mypy strict src: Success, no issues in 491 files
  - unresolved: full-suite run pending final wave gate
---

# verify

Focused suite green (74 tests: new quality/sufficiency/role-policy plus all
pre-existing context and selective-agentics tests unchanged). The eval corpus
covers the ready/degraded/sufficient/vetoed shapes. End-to-end smoke: a real
fixture capsule + ledger produces a measured report with the honest
unresolved split (cache_hit_rate, context_recall and per-token metrics stay
unresolved when their inputs are not recorded).
