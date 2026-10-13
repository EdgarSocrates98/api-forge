---
sdd: 1
feature: API_FORGE_ECONOMY_EVALS
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "165ee6e0cea0831a5bed5df7dd1e982d780a5ee63a8bc6bc5a0c034a4982a7c9"
results:
- gate: targeted tests
  outcome: pass
  evidence: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-evals-tests.txt
- gate: economy matrix
  outcome: pass
  evidence: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-matrix.json
- gate: Ruff
  outcome: pass
  evidence: ruff check + format on touched files
- gate: mypy
  outcome: pass
  evidence: 'Success: no issues found in 417 source files'
- gate: pytest full suite
  outcome: deferred
  evidence: runs once after the last wave, before push
---
# verify

48 runs (16 tasks × 3 profiles): quality 1.0 and 0 safety violations in every profile; mean calls 2.56 / 3.00 / 3.44 and fanout 0 / 0.44 / 0.88 for economy / balanced / deep; mutation 10/10; holdout 3/3 tasks pass. The first run found a real safety gap — sensitive tasks required a reviewer the catalog could not provide — fixed by letting `task-review` accept sensitive risk. One ground-truth error (relaxing `required` on a shared request/response schema is breaking) was corrected.
