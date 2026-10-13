---
sdd: 1
feature: API_FORGE_AGENTOPS_CONTROL_PLANE_2
phase: contract
profile: standard
status: done
upstream:
  path: intent.md
  sha256: "97cd4aa939d8d28b7a7185fca13d097889a7544274737e583ec1376bc765e8b0"
covers:
  - ControlRun/v1
  - ControlStep/v1
  - control-cli/v1
api_ir:
  input: Task id, named steps and dependency edges
  output: persisted run.json, events.jsonl and replay projection
---

# contract

`ControlRun/v1` registra status, steps, max_parallel, max_calls, calls_used e
revisão. `ControlStep/v1` registra dependências, status, attempts, retries,
erro e hash do resultado.

Estados terminais nunca podem ser reexecutados. Um run só vira `completed`
após todos os steps concluídos e verdict independente `approved`.
