---
sdd: 1
feature: API_FORGE_ECONOMY_CACHE_INCREMENTAL
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "3178ca56538354bc9d21440bb3e77425c4dcce7b702d909dfb2f184ab80e98c2"
results:
- gate: targeted tests
  outcome: pass
  evidence: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-tests.txt
- gate: cache eval
  outcome: pass
  evidence: sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL/evidence/cache-eval.json
- gate: Ruff
  outcome: pass
  evidence: ruff check + format on touched files
- gate: mypy
  outcome: pass
  evidence: 'Success: no issues found in 393 source files'
- gate: pytest full suite
  outcome: deferred
  evidence: runs once after the last wave, before push
---
# verify

10 corpus cases: warm hit rate 1.0, byte-identical vs `--no-cache`, zero stale reuse, invalidation precision and recall 1.0, delta recall 1.0. A comment appended to the contract or a class appended to `models.py` keeps every selection fresh; a `Money` constraint change invalidates exactly the four payment operations.
