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
| `api-forge-core` | Protocolo comum e roteamento |
| `api-forge-discovery` | Inventário e API-IR |
| `api-forge-contract` | Contratos e compatibilidade |
| `api-forge-architecture` | Workload e decisão de plataforma |
| `api-forge-data-access` | Relacionais/RDS, Redis, MongoDB, DynamoDB, Neptune, OpenSearch e Redshift |
| `api-forge-streaming` | Kafka/MSK, Kinesis, RabbitMQ, NATS e Pulsar |
| `api-forge-messaging` | SQS, SNS e EventBridge |
| `api-forge-verification` | Testes, segurança e resiliência |
| `api-forge-performance` | Carga, TPS e capacidade |
| `api-forge-observability` | Telemetria e operação |
| `api-forge-sdd` | SDD, tasks e gates |
| `api-forge-context` | TokenSave, Graphify e handoff |

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
