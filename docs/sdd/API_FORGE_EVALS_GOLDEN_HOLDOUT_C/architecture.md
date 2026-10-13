---
sdd: 1
feature: API_FORGE_EVALS_GOLDEN_HOLDOUT_C
phase: architecture
profile: standard
status: done
upstream:
  path: contract.md
  sha256: "8d5591a7ef772e9544f989e549e6a3b7ec8990b85c5f73123bbcfe82443f6d8e"
files:
  - src/apiforge/evals/suite.py
  - src/apiforge/cli.py
  - evals/cases/platform.yaml
  - tests/evals/test_platform_suite.py
decisions:
  - id: no-provider
    decision: eval runner não chama modelo nem rede
    rollback: manter somente validação YAML
  - id: evidence-first
    decision: required_evidence ausente produz BLOCKED
    rollback: nenhum; relaxar isso destruiria o gate
  - id: digest-holdout
    decision: mutation probe emite digest reprodutível
    rollback: marcar holdout como unresolved, nunca ignorar
---

# architecture

O suite loader valida dados declarativos; `evaluate_case` compara observado,
evidências e quality axes; `mutation_probe` gera uma referência de holdout sem
alterar a entrada. A CLI somente lista e valida a matriz.
