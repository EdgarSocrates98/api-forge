---
sdd: 1
feature: API_FORGE_EVALS_GOLDEN_HOLDOUT_C
phase: secure
profile: standard
status: done
upstream:
  path: verify.md
  sha256: "13ea189a539b55bf02e95b6cd746af6c9b3eca624560e69b58d1d8b0f842ea3e"
threat_model: docs/security/threat-model-mvp.md
---

# secure

Eval cases são dados locais. O runner não interpreta YAML como comando, não
chama rede e não promove alterações. Mutations são somente probes em memória.
