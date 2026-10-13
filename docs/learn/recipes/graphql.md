# Receita — ler um schema GraphQL SDL em IR canônico

**O quê:** `apiforge model graphql` extrai um schema GraphQL SDL para o
IR canônico.
**Por que:** o SDL é o contrato do grafo de tipos — o IR torna types,
queries, mutations e inputs comparáveis entre versões.
**Quando:** revisão de schema, onboarding de API GraphQL, pré-diff de
evolução.
**Quando não:** medir custo de query ou provar resolvers — o adapter lê
o schema, não a execução.

## Problema

"Preciso do mapa real do schema — quais types, operações e campos
existem?"

## Pré-requisitos

`apiforge` instalado; arquivo `.graphql`/`.gql` SDL no disco.

## Passo a passo

```bash
apiforge model graphql --path schema.graphql --detail-level full
```

## Saída esperada / interpretação

IR JSON com types, campos, operações raiz e diretivas — proveniência por
nó.

## Verificação

Breaking change de schema é julgamento de compatibilidade — o IR lista;
quem classifica é `apiforge diff contract` sobre contratos OpenAPI ou a
skill `api-forge-contract` para GraphQL.

## Limitações

Federation/subgraphs e diretivas custom saem como declaração; resolvers
e n+1 são runtime/código, fora do schema.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| schema rejeitado | SDL inválido | valide o SDL antes — o parser é estrito |

## Uso por agentes

Entregue o IR ao `api-contract-architect` — ele trabalha sobre a forma
canônica, não sobre o SDL cru.
