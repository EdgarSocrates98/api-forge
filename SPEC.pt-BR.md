# SPEC.md — API_FORGE_V1_CLOSURE

Fonte: `.claude/sdd/features/DESIGN_API_FORGE_V1_CLOSURE.md` (lint PASS)

Idioma: [English](SPEC.md) · [Português (Brasil)](SPEC.pt-BR.md)

## §G — lacunas fechadas

Fechar 9 lacunas residuais da v1: memória de performance, noise floor,
`suggest_fix`, 12 tipos de índice, pipeline de self-healing, vocabulário de
evals, matriz de laboratório, reconciliação de autonomia e rollback.

## §C — contratos

- determinístico, local-first e offline;
- nenhuma métrica fabricada; ausência é registrada, nunca preenchida;
- `suggest_fix` emite `ActionPlan/diff` e nunca altera o repositório;
- semântica de performance preservada: RPS ≠ TPS, saturação invalida,
  interpolação é proibida e baseline ausente é nomeado;
- todo verbo possui paridade CLI + dispatch + MCP somente leitura;
- pytest + ruff + mypy + release gate verdes ao final.

## §I — implementação

- `perf memory add|search` — `.apiforge/perf/runs.jsonl`;
- `perf suggest --case` — saída JSON `ActionPlan`;
- `perf verdict --noise-floor <dir>` — diretório de execuções baseline
  repetidas;
- `index build` — manifest com 12 tipos;
- `autonomy run --runbook self-healing` — pipeline de 8 etapas;
- `ActionPlan.proposed_diff` — campo opcional `str`, aditivo;
- `evals.yaml` — campo `type`, conjunto fechado de 11 valores;
- `tests/labs/matrix.yaml` — tecnologia × case → fixture/eval;
- `autonomy/modes.py` — constante `V1_MODE_MAP`.

## §R — fatos de design

| id | fato | fonte |
|----|------|-------|
| R1 | 3 modos + classes de política cobrem a semântica de 5 modos da v1; `V1_MODE_MAP` + ADR-010 tornam isso auditável | design D1 |
| R2 | noise floor = `(max-min)/mean` em pelo menos 2 execuções do mesmo assunto; menos de 2 → `None`, não provado | design D2 |
| R3 | `suggest` emite `ActionPlan`; `proposed_diff` é dado; o módulo não possui chamada de escrita | design D3 |
| R4 | 8 novos tipos de índice derivam de fatos existentes; vazio → arquivo vazio explícito | design D4 |

## §V — critérios de verificação

- V1 `suggest_fix` retorna `ActionPlan` ou diff; não existe caminho de escrita
  no módulo;
- V2 `noise_floor` é medido, nunca constante; menos de 2 execuções → `None`
  nomeado como não provado;
- V3 `|delta|` menor que o floor medido → verdict `inconclusive` com os dois
  valores;
- V4 o manifest de índices possui exatamente 12 tipos; os novos tipos são
  derivações de fatos, sem novos parsers;
- V5 etapas do heal: detect → explain → propose → authorize → execute → verify
  → compare → accept|rollback; cada transição é decidida por política e
  registrada em ledger;
- V6 heal executa somente verbos da dispatch table; a recusa nomeia
  requisitos ausentes;
- V7 `eval.type` fora do conjunto de 11 valores → recusa `AF-KNOW-EVAL-TYPE`;
- V8 cada célula da matriz resolve para fixture/eval real ou lacuna nomeada;
- V9 todo verbo novo aparece em CLI + dispatch + MCP somente leitura + testes
  de superfície;
- V10 derivações vazias → saída vazia explícita; ausência nunca é preenchida.

## §T — tasks concluídas

| id | status | objetivo | cobre |
|----|--------|----------|-------|
| T1 | x | `perf/run_store.py`: `runs.jsonl` append-only + busca por subject/tool/since | V10, `I.runsjsonl` |
| T2 | x | `perf/noise.py`: floor por métrica + wiring de `--noise-floor` | V2, V3 |
| T3 | x | `ActionPlan.proposed_diff` + `perf/suggest.py` sem escrita | V1, V9 |
| T4 | x | `index/build.py`: +8 tipos derivados, manifest de 12 tipos | V4, V10 |
| T5 | x | `autonomy/heal.py`: pipeline de 8 etapas sobre `policy.decide` + ledger | V5, V6 |
| T6 | x | `V1_MODE_MAP` + ADR-010 | V5, R1 |
| T7 | x | validação de tipo fechado no loader de knowledge | V7 |
| T8 | x | `tests/labs/matrix.yaml` + teste de cobertura | V8 |
| T9 | x | wiring CLI + dispatch + MCP + docs para os verbos novos | V9 |
| T10 | x | verificação completa: pytest, ruff, mypy e release gate | todos |

## §B — histórico

| id | data | causa | correção |
|----|------|-------|----------|
