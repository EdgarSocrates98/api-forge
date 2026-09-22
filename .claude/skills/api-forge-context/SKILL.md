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

