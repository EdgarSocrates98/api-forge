# API Forge Skills

As skills do API Forge seguem o padrão Agent Skills: cada skill é uma pasta com
`SKILL.md`, frontmatter mínimo e recursos opcionais. A fonte canônica está em
`.agents/skills/`, que é descoberta por Codex e hosts compatíveis. Os espelhos
`.claude/skills/`, `.devin/skills/` e `.github/skills/` atendem Claude Code,
Devin e Copilot.

## Princípios

- uma skill tem uma responsabilidade principal;
- agentes escolhem skills específicas, não uma skill monolítica;
- instruções comuns ficam em `AGENT_PROTOCOL.md`;
- conhecimento versionado fica em `knowledge/`;
- scripts são usados apenas para comportamento determinístico;
- referências extensas são carregadas sob demanda;
- toda skill deve declarar limites, entradas, saídas e gaps;
- nenhuma skill concede autoridade de segurança por si só;
- skills não devem conter credenciais, prompts secretos ou comandos destrutivos;
- mudanças de skills devem possuir evals e validação de mirrors.

## Skills iniciais

| Skill | Responsabilidade |
|---|---|
| `api-forge-core` | Protocolo comum e roteamento (entrada para qualquer tarefa de API) |
| `api-forge-discovery` | Inventário estático, API-IR, IaC e proveniência |
| `api-forge-contract` | OpenAPI/AsyncAPI/GraphQL/protobuf, compatibilidade e gRPC |
| `api-forge-architecture` | WorkloadProfile, decisão de plataforma, ADR, revisão AWS e migração de runtime |
| `api-forge-data-access` | Relacionais/RDS, Redis, MongoDB, DynamoDB, Neptune, OpenSearch e Redshift |
| `api-forge-messaging` | SQS, SNS, EventBridge e Step Functions |
| `api-forge-streaming` | Kafka/MSK, Kinesis, RabbitMQ, NATS e Pulsar |
| `api-forge-verification` | Plano de verificação, scanners allowlisted, segurança e resiliência |
| `api-forge-performance` | Plano de carga, scripts, veredito de TPS, regressão e profiling |
| `api-forge-observability` | OTel, SLO/alertas, vendors (Datadog/Dynatrace/CloudWatch) e autonomia/runbooks |
| `api-forge-sdd` | Risco e perfil, fases, TaskSpecs, gates por evidência e field validation |
| `api-forge-context` | Funnel, capsules, delta, grafo, handoff e economia (detalhe em `references/economy.md`) |
| `api-forge-platform-completion` | Prontidão da plataforma, capability matrix, change-control e manutenção de agents/skills |

## Formato de uma skill

Cada `SKILL.md` segue o mesmo esqueleto, para que qualquer host leia igual:

- frontmatter com `name`, `description` (o que faz, quando usar com frases
  reais e quando **não** usar, apontando a skill vizinha), `compatibility` e
  `metadata.version`; use `>-` para textos longos (evita erro de YAML com `:`);
- propósito em um parágrafo explicando o porquê;
- "Antes de começar" apontando para `api-forge-core`/`AGENT_PROTOCOL.md`;
- procedimento numerado com comandos reais do CLI;
- guardrails com a razão de cada um;
- entrega e especialistas típicos (`agents/*.md`).

Conteúdo extenso vai para `references/` dentro da skill e é carregado sob
demanda. Todo comando citado precisa existir no `--help` do CLI.

## Compatibilidade

O corpo das skills usa Markdown, caminhos relativos e comandos CLI neutros.
Não use campos exclusivos de Claude, Codex, Devin ou Copilot dentro do caminho
principal. Extensões específicas devem ficar em diretórios opcionais do host.

O mapa de lacunas, dependências e fases do produto está em
[docs/API_FORGE_EVOLUTION_MAP.md](API_FORGE_EVOLUTION_MAP.md). Skills novas devem
ser adicionadas por especialidade e acompanhadas de evals, limites, evidências e
validação de mirrors; não crie uma skill monolítica para cobrir todas as fases.

## Validação

Execute:

```powershell
python scripts/validate_skills.py
python scripts/sync_skills.py
python scripts/validate_skills.py --check-mirrors
```
