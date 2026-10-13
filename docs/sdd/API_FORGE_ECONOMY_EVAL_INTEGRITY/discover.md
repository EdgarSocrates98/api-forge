---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: discover
profile: critical
status: draft
approaches:
- id: targeted-fixes-with-mutation-tests
  summary: floor and baseline gates, declarative token eligibility, run-scoped failures, production-path oracle, confined explicit paths
  verdict: chosen -- small diff, each fix proven by a test that fails on the old bug
- id: common-eval-oracle-framework
  summary: shared base for every eval
  verdict: refused -- large refactor beyond the requested follow-ups
chosen: targeted-fixes-with-mutation-tests
---
# discover

Source: `prompt_evo_new_economy.md` (review of `main` @ `6d2f263`, verdict `PASS COM FOLLOW-UPS`): four follow-ups on the layer that measures and certifies the economy.
