# API Forge Economy — gastar só o necessário, com prova

[English](API_FORGE_ECONOMY.en.md) · [Catálogo de códigos](../catalog-contract.md) · [Uso da plataforma](API_FORGE_PLATFORM_USAGE.md)

O programa de economia (`prompt_evo_economy.md`, ondas 0–8) reduz contexto,
chamadas, ferramentas e verificação ao mínimo suficiente **sem economizar
segurança nem evidência**. Tudo é determinístico, offline e read-only; nenhum
verbo chama provider, executa testes ou muta infraestrutura.

## Invariantes que nunca entram no orçamento

- verificação de contrato, checagem de breaking change, auth/segurança quando relevantes;
- proveniência, política crítica, verificação pós-mudança e relato de `unresolved`;
- esgotar um orçamento vira `unresolved` com código `AF-*`, nunca downgrade silencioso;
- fases SDD `contract`, `verify` e `secure` são protegidas: estouro é reportado, nunca cortado.

## Mapa por pergunta

| Pergunta | Comando | Contrato |
|---|---|---|
| Quanto esta run gastou e por quê? | `apiforge economy report`, `economy stats [--run-id R]`, `economy explain <run>` | `RunLedgerEntry/v1` |
| Qual o mínimo de contexto para uma operação? | `apiforge context capsule --target "POST /orders"`, `context expand ctx://sha256/<hex>` | `ContextCapsule/v1` |
| Qual perfil usar? | `apiforge runtime run <task> --profile economy\|balanced\|deep`, `sdd classify` | `EconomyPlan/v1`, `BudgetEnvelope/v1` |
| O que mudou desde a última análise? | `apiforge context delta`, `cache stats\|invalidate`, `context gc`, `--no-cache` | `CacheEntry/v1`, `DeltaSlice/v1` |
| Qual knowledge pack carregar? | `apiforge knowledge select --intent "..."`, `knowledge search --query "..."` | `ExpertiseSelection/v1`, `RetrievalResult/v1` |
| Como enxugar debate e agentes? | `apiforge debate packet`, `agents audit` | `RefereePacket/v1`, `AgentUniqueness/v1` |
| Como reduzir saída de ferramentas? | `apiforge --output compact <verb>`, `slice tests\|log`, `mcp surface`, `apiforge-mcp --surface compact` | `TestSlice/v1`, `ErrorSlice/v1`, `ToolSurface/v1` |
| Quais testes rodar? | `apiforge verify plan --changed F --risk R` | `VerificationPlan/v1` |
| Teste inconclusivo — e agora? | `apiforge verify escalate --static likely --test inconclusive` (ou `--test-slice`) | `VerificationEscalation/v1` |
| Preciso de evidência de produção? | `apiforge evidence gate --question "..." [--offline]` | `LiveEvidenceDecision/v1` |
| Como citar evidência sem trazer tudo? | `apiforge evidence resolve evidence://finding/<id>` | `EvidenceNode/v1` |
| Algum knowledge pack venceu? | `apiforge knowledge watch --manifest upstream.json --now <iso>` | `FreshnessWatch/v1` |
| Quanto cada fase SDD pode gastar? | `apiforge economy phase-budget --profile P [--usage U]` | `PhaseBudgetPlan/v1` |
| Quanto a run já gastou antes do resume? | `apiforge runtime checkpoint <task> <run>` | `EconomyCheckpoint/v1` |
| O setup está pagando demais? | `apiforge economy doctor`, `economy tier`, `economy roi` | `EconomyDoctor/v1`, `TierDecision/v1`, `RoleROI/v1` |

## Fluxo recomendado para um agente

1. `sdd classify` define o risco; o risco define o piso de perfil.
2. `context capsule` em vez do case inteiro; `context expand` só sob demanda.
3. `knowledge select` carrega só packs com gatilho; `knowledge search --tier 1` primeiro.
4. Antes de chamar AWS/Datadog/CloudWatch/GitHub: `evidence gate`. Pergunta sobre o
   artefato fica local; só efeito em runtime ganha `live_read_only` (com receipt).
5. Depois de mudar: `verify plan` escolhe V0–V5 e os testes impactados.
6. Resultado inconclusivo: `verify escalate`. Teste conclusivo encerra; runtime
   read-only só após teste inconclusivo; nunca mutação.
7. Retomada: `runtime resume` mantém ao menos o perfil do `economy_checkpoint.json`
   e soma as chamadas já gastas.

## Frescor de knowledge (refresh separado do runtime)

O runtime usa knowledge local validado. Um workflow separado grava um manifest
local `{"sources": {"<upstream>": {"fingerprint", "version", "observed_at"}}}`.
Packs declaram em `pack.yaml`:

```yaml
freshness:
  upstream: openapi-spec
  source_hash: "sha256-do-upstream-validado"
  source_version: "3.1.0"
  expires_at: "2027-01-01T00:00:00+00:00"
  window_days: 180
```

`knowledge watch` marca `refresh_needed` apenas quando fingerprint, versão,
expiração ou janela (medida a partir de `verified`) dizem que está vencido.

## Cache

`APIFORGE_CACHE=off` desliga as camadas de cache (qualquer outro valor é o
diretório de cache); `--no-cache` faz o mesmo por comando e produz saída
idêntica. `APIFORGE_CACHE_HOME` habilita o tier compartilhado entre
repositórios; todo objeto é re-hasheado na leitura.

## Mudar política econômica

Antes de alterar perfis, roteamento ou cortes:

```bash
apiforge evals economy-matrix --out antes.json
# aplique a mudança
apiforge evals economy-matrix --out depois.json
apiforge evals gate --baseline antes.json --candidate depois.json
```

Qualquer regressão de segurança rejeita. Benchmarks por onda:
`evals economy`, `economy-routing`, `cache`, `selective-agentics`,
`tool-economy`, `economy-extras`, `economy-freshness`, `replay`.

## Limitações

- Tokens só são `observed` com transcript; sem ele ficam `unresolved`.
- Classificação de perguntas e seleção de testes são declaradas por termos e
  símbolos; recall primeiro, o piso do ladder limita o custo.
- Uso por fase SDD é informado em JSON; atribuição automática pelo ledger é
  trabalho futuro.
