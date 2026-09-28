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

## Agentes seletivos

- Especialista recebe só o subconjunto `focused` do capsule; revisor, crítico e referee recebem menos (`role-context.json`). Não repasse o contexto pai inteiro a subagentes.
- Carregue expertise só pelos packs de `apiforge knowledge select --intent "..."`; `no-expertise-trigger` significa não carregar nada.
- Em debate, submeta `--disagree point=reason`, `--risk`, `--confidence` e entregue ao referee `apiforge debate packet`, não as posições completas.
- `apiforge agents audit` aponta agentes sem nada único; é evidência para decisão humana, não remoção automática.

## Saída e ferramentas econômicas

- Pergunta sobre artefato → verbo do Forge antes de ler arquivos (`apiforge agentops projection --host <host>` lista o `verb_map`).
- Use `apiforge --output compact <verbo>` (ou `APIFORGE_OUTPUT=compact`): remove só null/vazio, sem perda.
- Falha de teste ou CI: `apiforge slice tests --input <log>` / `apiforge slice log --input <log>`; expanda o `log_ref` só se precisar.
- MCP compacto: `apiforge-mcp --surface compact` expõe 6 gateways; ache a ferramenta com `apiforge_discover` e execute com `apiforge_call`.

## Verificar, buscar e citar com economia

- Depois de mudar arquivos: `apiforge verify plan --changed <arquivo> --risk <micro|low|medium|high>` dá o nível V0–V5 e só os testes impactados; não rode a suíte inteira salvo V5.
- Conhecimento: `apiforge knowledge search --query "..."` devolve 3 trechos ranqueados; peça `--tier 2` só se não bastar.
- Evidência: `apiforge evidence resolve evidence://finding/<id>` traz um salto por vez; siga os `neighbors` sob demanda.
- `apiforge economy doctor` aponta configurações que encarecem runs; `apiforge economy tier` só barateia modelo com benchmark.
- Antes de consultar AWS/Datadog/CloudWatch/GitHub: `apiforge evidence gate --question "..."`; pergunta estática fica no OpenAPI/código local, só pergunta de efeito em runtime ganha `live_read_only` (nunca mutação).
- Teste inconclusivo? `apiforge verify escalate --static likely --test inconclusive` diz o próximo passo; teste conclusivo encerra.
- Knowledge vencido: `apiforge knowledge watch --manifest <upstream.json> --now <iso>` lista só os packs `refresh_needed`; o refresh é outro workflow.
- Ao retomar: `apiforge runtime checkpoint <task> <run>` mostra o gasto já feito; o resume nunca baixa o perfil. Orçamento por fase SDD: `apiforge economy phase-budget --profile <p>`.

## Mudar política econômica

- Antes de alterar perfis, roteamento ou cortes: `apiforge evals economy-matrix --out antes.json`, aplique a mudança, gere `depois.json` e rode `apiforge evals gate --baseline antes.json --candidate depois.json`; só siga com `ship`.
- `apiforge evals replay --corpus evals/corpus/economy-replay` mostra o efeito em runs guardados sem chamar provedor; `apiforge economy roi` mostra se agentes extras mudam o resultado.

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

