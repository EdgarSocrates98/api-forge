---
name: api-forge-context
description: >-
  Reduz contexto sem perder prova — context funnel, capsules `ctx://` por
  operação, delta-first em PR, cache por dependência, TokenSave, grafo de
  proveniência e Graphify — e produz handoffs verificáveis no formato Outcome
  Brief. Use em sessões longas, contexto grande ou perto do limite, múltiplos
  agentes/subagentes, análise de impacto ("o que esta mudança afeta?"),
  retomada de run, compactação, handoff entre hosts, economia de tokens ou
  quando a tentação for "ler o repositório inteiro". Não use para decidir o
  que testar (→ api-forge-verification) nem para conduzir as fases de uma
  feature (→ api-forge-sdd).
compatibility: >-
  Funciona sobre o armazenamento local do API Forge (`.apiforge/`); requer o
  CLI `apiforge`. Não exige banco vetorial, serviço externo nem provedor de
  modelo.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — contexto, impacto e handoff

Contexto é orçamento. Ler o repositório inteiro custa caro e piora a
resposta, porque a evidência relevante se dilui. Esta skill troca leitura
ampla por perguntas ao core, que devolve a evidência mínima suficiente com
hash, e garante que o que sai num handoff seja tão verificável quanto o que
entrou.

## Context funnel

Carregue nesta ordem e pare assim que a pergunta estiver respondida:

1. caso e manifesto;
2. inventário;
3. facts candidatos;
4. findings e regras;
5. subgrafo de impacto;
6. símbolos/trechos mínimos;
7. testes e evidências;
8. conhecimento específico;
9. decisão e próximo passo.

`apiforge context funnel` mede quantos bytes cada estágio mantém. Nunca leia
o repositório inteiro se API-IR, facts, capsule ou grafo resolverem.

## Capsule: verbo antes de Read

Para uma pergunta sobre uma operação, com o caso já analisado:

```text
apiforge context capsule --target "POST /payments" [--budget-bytes N] [--level L0..L4] [--impact direct|transitive|all]
apiforge context expand ctx://sha256/<hex> --run-id <run_id>
```

- O capsule traz refs `ctx://` (operação, schemas, handler, model em
  `parity`/`delta`, findings, testes); expanda só o que a pergunta exige.
- `status: unresolved` + `AF-CONTEXT-BUDGET-EXHAUSTED` é parcial explícito:
  aumente o orçamento ou baixe o nível; nunca complete lendo o repositório
  em silêncio.
- `status: degraded` + `AF-CTX-GRAPH-UNAVAILABLE`: rode `apiforge analyze`
  antes.
- `unresolved: code-route-missing:*` indica drift contrato ↔ código, não
  falha do gateway.

## Delta primeiro e cache

Em PR ou mudança local, comece pelo delta:

```text
apiforge context delta --base <ref> [--head <ref>]     # ou --changed <arquivo> ... sem git
apiforge cache stats | apiforge cache invalidate --changed <arquivo>
apiforge context gc [--apply]
```

- `capsule_targets` do delta dizem quais capsules montar; `unmapped:<path>`
  é explícito — não ignore.
- O cache é consultivo: reuso só com dependências inalteradas; a saída é
  idêntica a `--no-cache`.
- `AF-DELTA-GIT-UNAVAILABLE` → use `--changed`; `AF-CACHE-LAYER-DISABLED` →
  a camada ainda não tem chamador.

## Impacto e grafo

```text
apiforge index build | apiforge index status            # TokenSave: índices por hash
apiforge graph build --case .apiforge/case --out .apiforge/graph
apiforge graph impact --graph .apiforge/graph --node <id> [--max-depth 4]
apiforge graph trace ...  |  apiforge graph coverage ...
```

O grafo relaciona artefatos, operações, handlers, bancos, regras, findings,
tasks, testes, traces, decisões e releases por arestas de dependência,
implementação, evidência, impacto, violação e verificação. Caminho ausente
é nomeado, não presumido. Em multi-repo, `apiforge workspace locality`
carrega o repo alvo primeiro, vizinhos diretos depois, transitivos só sob
pedido.

## Agentes seletivos

- Especialista recebe só o subconjunto `focused` do capsule; revisor,
  crítico e referee recebem menos (`role-context.json`). Não repasse o
  contexto pai inteiro a subagentes.
- Expertise só pelos packs de `apiforge knowledge select --intent "..."`;
  `no-expertise-trigger` significa não carregar nada.
- Em debate, submeta `--disagree point=reason`, `--risk`, `--confidence` e
  entregue ao referee `apiforge debate packet`, não as posições completas.
- `apiforge agents audit` aponta agentes sem nada único; é evidência para
  decisão humana, não remoção automática.

## Economia avançada

Para verificar/buscar/citar com economia, saída compacta, slicers de log,
MCP compacto, prova de economia e mudança de política econômica, leia
`references/economy.md`. Regra que não muda: budgets nunca cortam contract,
verify, secure, provenance nem o relato de `unresolved`.

## Handoff

Todo handoff (entre agentes, hosts ou sessões) usa o Outcome Brief:

```text
Status:
Outcome:
Human action:
Proof:
Gaps:
Next:
Open:
```

Preserve a diferença entre evidência **direta** (você observou), **derivada**
(o core calculou de algo observado) e **reportada** (alguém disse). Um resumo
nunca é mais autoritativo que sua fonte: cite o `ctx://`, `fact_id` ou
receipt de onde veio. Ao retomar, leia `apiforge runtime checkpoint <task> <run>`
antes de agir.
