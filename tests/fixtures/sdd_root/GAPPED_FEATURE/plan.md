---
sdd: 1
feature: GAPPED_FEATURE
phase: plan
profile: quick
status: ready
upstream:
  path: intent.md
  sha256: "694bfd0ba5f0d468b61131da30e7fa906ff0e0277359694fe46662048de3ec5c"
tasks:
  - name: implement-x
    covers: [s1]
    test: gapped/missing_test.py
---
# Plan
