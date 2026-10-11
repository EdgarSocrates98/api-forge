# Receita — descobrir o que um projeto FastAPI realmente expõe

**O quê:** `apiforge model build` compõe o API-IR canônico cruzando o
documento OpenAPI 3.1 com o projeto FastAPI.
**Por que:** o IR é a base de todo o resto — diff, judge, verify e case
falam de rotas e schemas reais, não de chute.
**Quando:** onboarding de repo desconhecido, inventário de endpoints,
pré-revisão.
**Quando não:** serviço sem contrato OpenAPI — aí é `apiforge analyze` com
descoberta de rotas do código, e o IR fica parcial por declaração.

## Problema

"Herdou um FastAPI de 40 rotas — o que ele expõe de fato?"

## Pré-requisitos

`apiforge` instalado; `openapi.yaml` exportado do app (ou o documento de
contrato mantido no repo) + o root do projeto.

## Passo a passo

```bash
apiforge model build --contract api/openapi.yaml --project . \
  --detail-level full
# o case-store fica FORA do projeto analisado (overlap é recusado)
apiforge analyze --contract api/openapi.yaml --project . \
  --out-dir /caminho/absoluto/fora/do/projeto
apiforge next-step --findings <out-dir>/findings.json --phase verify
```

## Saída esperada / interpretação

API-IR JSON: rotas, schemas, handlers e dependências com proveniência.
`analyze` grava o case no `--out-dir` com hashes; `next-step` roteia
os findings para o especialista.

## Verificação

O case deve existir no `--out-dir` — `next-step` devolve
`AF-ROUTING-NO-FINDINGS` se nada foi persistido, e isso é a prova de que
o analyze rodou de verdade.

## Limitações

Descoberta estática: middleware, rotas montadas em runtime e dependências
injetadas dinamicamente podem ficar `unresolved` — declarado no IR.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| IR vazio | contrato errado vs projeto | confirme que o `openapi.yaml` é o do app |
| rota ausente | prefixo/router condicional | verifique `unresolved` no IR, não o silêncio |

## Uso por agentes

O IR é o artefato que os coordenadores consomem — nunca releia o código
inteiro quando `model build` já provou o mapa.
