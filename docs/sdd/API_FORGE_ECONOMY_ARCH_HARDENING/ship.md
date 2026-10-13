---
sdd: 1
feature: API_FORGE_ECONOMY_ARCH_HARDENING
phase: ship
profile: critical
status: draft
upstream:
  path: benchmark.md
  sha256: "63bfe3a913bc81a5b700299eb3088430e026c31311c41e02d194d87bfce7cb08"
deviations:
- ci-merged-commits-need-apiforge-pr-token
- shadow-mode-declared-by-taskspec-input
evidence:
- path: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/agentic-quality-eval.json
  sha256: 9ddb21443783b866ac15dcd176791fbe84ac5ad68f93b94d36a5fc2b120db87f
- path: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/economy-hardening-eval.json
  sha256: 8e50da16ce754b846f7a3d9cc60b8d16c24c361b333ee6b36d94238a66b84544
- path: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/hardening-tests.txt
  sha256: 55b7eb20ca6d5e3ae00e83906efdc1ee387f820cb7e822fb17dd8d58cf8b2449
---
# ship

Ready for review. CI runs on merged commits only when the repository secret `APIFORGE_PR_TOKEN` is configured; otherwise the daily scheduled run validates `main`. Shadow mode is declared with the TaskSpec input `shadow_mode=capability_eval`.
