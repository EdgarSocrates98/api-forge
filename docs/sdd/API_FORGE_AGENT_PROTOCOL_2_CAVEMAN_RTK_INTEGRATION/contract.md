---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: contract
profile: standard
status: done
upstream:
  path: intent.md
  sha256: "f2758a9340eb8a31d6858cc737798f0bf46a2385b231758be337355051b85282"
covers:
  - CompactedOutput/v1
  - CavemanMode/v1
  - context-compact-cli/v1
api_ir:
  input: UTF-8 command output artifact
  output: CompactedOutput/v1 JSON
---

# contract

`CompactedOutput/v1` contém `command`, `text`, `mode`, bytes e linhas antes e
depois, `omitted_lines`, contagem de linhas críticas, `source_sha256`,
`artifact`, `critical_evidence_preserved` e `loss_policy`.

Os modos são `off`, `lite`, `full`, `ultra` e `wenyan`. O modo apenas controla
a projeção de transporte; não muda o artefato de origem nem a semântica de
contratos, findings, evidências, código ou dados.

`context compact` é somente leitura e aceita `--input`, `--command`, `--mode`,
`--max-lines` e `--detail-level`.
