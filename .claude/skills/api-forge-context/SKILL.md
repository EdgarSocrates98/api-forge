---
name: api-forge-context
description: Reduz contexto sem perder prova usando TokenSave, context funnel e Graphify, e produz handoffs verificáveis no formato Outcome Brief. Use em sessões longas, múltiplos agentes, análise de impacto, compactação, handoff, memória ou quando o contexto estiver grande.
compatibility: Funciona com o armazenamento local do API Forge; não exige banco vetorial, serviço externo ou provedor de modelo.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Context funnel

Carregue nesta ordem:

1. caso e manifesto;
2. inventário;
3. facts candidatos;
4. findings e regras;
5. subgrafo de impacto;
6. símbolos/trechos mínimos;
7. testes e evidências;
8. conhecimento específico;
9. decisão e próximo passo.

Use cache por hash, deduplicação e `detail_level`. Nunca leia o repositório inteiro se API-IR, facts ou Graphify resolverem a pergunta.

## Context Gateway (verbo antes de Read)

Para uma pergunta sobre uma operação, com o caso já analisado:

```text
apiforge context capsule --target "POST /payments" [--budget-bytes N] [--level L3|L4]
apiforge context expand ctx://sha256/<hex> --run-id <run_id>
apiforge economy stats --run-id <run_id>
apiforge economy explain <run_id>
```

- O capsule traz refs `ctx://` (operação, schemas, handler, model em `parity`/`delta`, findings, testes); expanda só o que a pergunta exige.
- `status: unresolved` + `AF-CONTEXT-BUDGET-EXHAUSTED` é resultado parcial explícito: aumente o orçamento ou baixe o nível; nunca complete lendo o repositório inteiro em silêncio.
- `status: degraded` + `AF-CTX-GRAPH-UNAVAILABLE`: rode `apiforge analyze` antes.
- `unresolved: code-route-missing:*` indica drift contrato↔código, não falha do gateway.
- Tokens só existem com transcript (`economy stats --transcript`); bytes não são tokens.

## Delta primeiro e cache

Em PR ou mudança local, comece pelo delta, não pelo repositório:

```text
apiforge context delta --base <ref> [--head <ref>]   # ou --changed <arquivo> ... sem git
apiforge cache stats | apiforge cache invalidate --changed <arquivo>
apiforge context gc [--apply]
```

- `capsule_targets` do delta dizem quais `context capsule` montar; `unmapped:<path>` é explícito, não ignore.
- O cache é consultivo: reuso só com dependências inalteradas (arquivo, span, ponteiro do contrato, vizinhança do grafo); a saída é idêntica a `--no-cache`.
- `AF-DELTA-GIT-UNAVAILABLE` → use `--changed`; `AF-CACHE-LAYER-DISABLED` → a camada não tem chamador ainda.

## Graphify

Relacione artefatos, operações, handlers, bancos, regras, findings, tasks, testes, traces, decisões e releases por edges de dependência, implementação, evidência, impacto, violação e verificação.

## Handoff

Use:

```text
Status:
Outcome:
Human action:
Proof:
Gaps:
Next:
Open:
```

Preserve a diferença entre evidência direta, derivada e reportada. Um resumo não é mais autoritativo que sua fonte.

