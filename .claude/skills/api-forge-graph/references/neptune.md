# Amazon Neptune — referência operacional

Carregue para perguntas de serviço: qual Neptune, como autenticar, como
carregar, como coletar plano com segurança. Conhecimento aqui orienta a
análise; postura real vem de dump (`collect neptune` → `model neptune`) e
recomendações de IAM/VPC/Terraform pertencem a `api-infra-reviewer`.

## Sumário

- Neptune Database vs Neptune Analytics
- Versões de engine
- Endpoints
- Autenticação: IAM e SigV4
- Rede
- Bulk loader
- Neptune Streams
- Backup e snapshots
- Métricas CloudWatch
- Custo (qualitativo)
- `collect neptune-explain`: allowlist e guardas
- Redação de dumps
- Fontes

## Neptune Database vs Neptune Analytics

| | Neptune Database | Neptune Analytics |
|---|---|---|
| Uso | OLTP de grafo atrás de API | análise em memória, algoritmos, vetores |
| Linguagens | Gremlin, openCypher (property graph), SPARQL (RDF) | openCypher |
| Topologia | cluster: 1 writer + até 15 réplicas, storage compartilhado; ou serverless | grafo único, capacidade em memória provisionada |
| Algoritmos | não nativos | `CALL neptune.algo.*`, `neptune.algo.vectors.*` |
| Carga | bulk loader de S3, escrita por query | import de S3 ou de cluster Neptune, escrita por query |

Regras AF-GDB-009/010 só fazem sentido no Analytics (`performance.md`).

## Versões de engine

As linhas 1.2.x, 1.3.x e 1.4.x estão em uso; recursos (openCypher
completo, I/O-Optimized, DFE, parâmetros, retenção de Streams) dependem da
versão. Sempre leia a versão no dump de cluster (`EngineVersion`) antes de
afirmar suporte e confira as release notes da versão exata. O pack
`knowledge/neptune` mantém a matriz declarada.

## Endpoints

- **Cluster (writer)** — escrita e leitura com consistência imediata.
- **Reader** — balanceia entre réplicas; leitura com lag de replicação.
- **Instância** — endpoint de uma réplica específica; útil para isolar
  carga analítica ou PROFILE.
- Endpoints HTTPS por linguagem: `/gremlin`, `/openCypher`, `/sparql`,
  além de `/gremlin/explain`, `/gremlin/profile`, `/loader`, `/status`
  e endpoints de Streams.

## Autenticação: IAM e SigV4

- Com IAM database authentication ativo, toda requisição precisa de
  assinatura SigV4 (serviço `neptune-db`); o SDK (`boto3` `neptunedata`)
  e os plugins de SigV4 dos drivers Gremlin fazem a assinatura.
- Ações IAM de dados são do prefixo `neptune-db:` (ex.:
  `ReadDataViaQuery`, `WriteDataViaQuery`, `DeleteDataViaQuery`,
  `GetQueryStatus`). Conceder só leitura ao papel do coletor é
  recomendação para `api-infra-reviewer`.
- Credencial nunca é lida nem gravada pelo API Forge; o receipt do coletor
  guarda `query_sha256` e endpoint, não credenciais.

## Rede

Neptune Database é acessível só dentro da VPC (sem endpoint público por
padrão): o cliente precisa de rota, security group e, para o loader,
VPC endpoint de S3. Diagnóstico de conectividade é de infra; a skill só
registra o gap ("coletor sem rota até o cluster").

## Bulk loader

- Endpoint `/loader` (ou `neptunedata.start_loader_job`); lê de S3 usando
  um **IAM role associado ao cluster** com leitura no bucket.
- Formatos: property graph — CSV do formato Gremlin (`format: csv`,
  cabeçalhos `~id`, `~label`, `~from`, `~to`, `nome:Tipo`) e CSV openCypher
  (`format: opencypher`); RDF — `ntriples`, `nquads`, `rdfxml`, `turtle`.
- Parâmetros relevantes: `failOnError`, `parallelism`, `updateSingleCardinalityProperties`,
  `queueRequest`. Status via `get_loader_job_status`.
- Carga é mutação: o API Forge gera arquivos (`graph export`), nunca dispara
  o loader. Ver `system-graph-bridge.md`.

## Neptune Streams

Log ordenado de mudanças (property graph e RDF) habilitado pelo parâmetro
de cluster `neptune_streams`; consumido por polling HTTP ou pelo consumidor
Lambda de referência. Retenção configurável por versão (padrão de 7 dias).
Útil para invalidar cache e replicar para busca; o desenho do consumidor é
de `api-event-driven-architect`.

## Backup e snapshots

Backup contínuo com retenção configurável e restauração point-in-time;
snapshots manuais persistem até serem apagados e podem ser copiados entre
regiões/contas. Restaurar cria **novo** cluster. Verifique no dump:
retenção, criptografia em repouso (`StorageEncrypted`, chave KMS) e
proteção contra deleção.

## Métricas CloudWatch

Conhecimento para leitura de dumps/consultas; a projeção de monitores é de
`api-observability-integration-engineer`.

| Métrica | Leitura |
|---|---|
| `CPUUtilization`, `FreeableMemory` | saturação da instância |
| `BufferCacheHitRatio` | working set fora do cache → I/O de storage |
| `MainRequestQueuePendingRequests` | fila de requisições; concorrência acima da capacidade |
| `GremlinRequestsPerSec`, `OpenCypherRequestsPerSec`, `SparqlRequestsPerSec` | volume por linguagem |
| `ClusterReplicaLag` | lag das réplicas (leitura-após-escrita) |
| `NumTxCommitted`, `NumTxRolledBack` | conflito de escrita (supernó, MERGE concorrente) |
| `VolumeBytesUsed` | crescimento do storage |

## Custo (qualitativo)

Sem calculadora numérica: preço varia por região e muda. Fatores:

- classe e quantidade de instâncias (writer + réplicas) ou capacidade
  serverless (NCU);
- configuração de storage: **Standard** (cobra I/O) vs **I/O-Optimized**
  (sem cobrança por I/O, instância/storage mais caros) — I/O alto favorece
  I/O-Optimized;
- storage consumido, backups além do incluído, transferência;
- Analytics: capacidade em memória provisionada (m-NCU) enquanto o grafo
  existe, independentemente de uso.

## `collect neptune-explain`: allowlist e guardas

Operações `neptunedata` permitidas (frozenset; qualquer outra →
`AF-GDB-COLLECT-OP` antes de criar o cliente):

| Modo | Operação | Executa? |
|---|---|---|
| Gremlin padrão | `execute_gremlin_explain_query` | não |
| openCypher padrão | `execute_open_cypher_explain_query` com `explainMode=static` | não |
| Gremlin `--profile` | `execute_gremlin_profile_query` | **sim** |
| openCypher `--profile` | `execute_open_cypher_explain_query` com `explainMode=dynamic` | **sim** |
| SPARQL | — (`neptunedata` não tem explain SPARQL) | `AF-GDB-EXPLAIN-SPARQL`: importe dump |

Guardas, todas avaliadas antes de qualquer chamada de rede:

- texto com mutação → `AF-GDB-PROFILE-MUTATION` (vale também sem
  `--profile`);
- `--profile` sem `--reader-endpoint` igual a `--endpoint` →
  `AF-GDB-PROFILE-READER`; o receipt registra `reader_declared`, não
  verificado;
- `--profile` com texto dinâmico → `AF-GDB-PROFILE-DYNAMIC`;
- argumento ausente/inválido → `AF-GDB-COLLECT-ARG`.

O dump vai para `--out` com `CollectManifest` (`operation`,
`executes_query`, `query_sha256`, endpoint, `profile`) e é consumido por
`model graph-explain`. Falha AWS ou `boto3` ausente: `AF-COLLECT-AWS`.

## Redação de dumps

Explain e profile ecoam o texto da query, incluindo literais (e-mails, ids,
tokens em filtros). Antes de commitar um dump real: substitua literais por
marcadores, mantenha a estrutura de operadores e registre que houve
redação. Prefira parâmetros na query para que o dump já saia sem valores.

## Fontes

- Neptune User Guide: https://docs.aws.amazon.com/neptune/latest/userguide/intro.html
- Neptune Analytics User Guide: https://docs.aws.amazon.com/neptune-analytics/latest/userguide/what-is-neptune-analytics.html
- IAM auth e ações `neptune-db`: https://docs.aws.amazon.com/neptune/latest/userguide/iam-dp-actions.html
- Bulk loader: https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load.html
- Neptune Streams: https://docs.aws.amazon.com/neptune/latest/userguide/streams.html
- Backup e restauração: https://docs.aws.amazon.com/neptune/latest/userguide/backup-restore.html
- Métricas CloudWatch: https://docs.aws.amazon.com/neptune/latest/userguide/cw-metrics.html
- Storage I/O-Optimized: https://docs.aws.amazon.com/neptune/latest/userguide/storage-types.html
- Engine releases: https://docs.aws.amazon.com/neptune/latest/userguide/engine-releases.html
- boto3 `neptunedata`: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptunedata.html
