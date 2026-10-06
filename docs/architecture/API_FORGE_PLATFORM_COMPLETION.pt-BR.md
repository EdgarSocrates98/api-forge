# Arquitetura de conclusão da plataforma API Forge

Idioma: [English](API_FORGE_PLATFORM_COMPLETION.md) · [Português (Brasil)](API_FORGE_PLATFORM_COMPLETION.pt-BR.md)

O API Forge é um control plane determinístico para trabalho de engenharia de
software. Suas superfícies podem aceitar uma intenção em linguagem natural,
mas a fronteira de execução é sempre uma requisição tipada, um case
persistido, uma decisão de política e um artefato verificável.

```text
CLI / MCP / IDE / UI
          │
          ▼
CapabilityRequest/v1 → supervisor determinístico → AgentArtifact/v1
          │                       │                         │
          ▼                       ▼                         ▼
       case/IR              policy + adapters       evidence + unresolved
          └───────────────────────┴──────────────────────────┘
                                  ▼
                         graph → receipt → brief
```

O core não importa SDKs de modelos, cloud, banco ou broker. Integrações
externas usam o gateway read-first. Qualquer mutação exige decisão de
política, aprovação, rollback e receipt. Um provedor sem prova permanece
`unsupported` ou `unresolved`.

Os mesmos contratos `CapabilityRequest` e `CapabilityResult` são projetados
por CLI, MCP, IDE e UI. A apresentação pode mudar; estado de suporte,
evidência, lacunas e semântica de segurança não podem.

O conjunto inicial de provas cobre APIs, bancos, mensageria, CI/CD, cloud e
front-end com uma fixture, um golden e um holdout por vertical. O holdout é
essencial: comprova que agentes e adapters preservam a incerteza em vez de
fabricar uma resposta otimista.

Comandos operacionais, localização de fixtures e fronteira de suporte de
produção estão em [Uso da plataforma](../guides/API_FORGE_PLATFORM_USAGE.md).
