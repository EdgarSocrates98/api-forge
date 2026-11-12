---
name: api-forge-sentinel
description: >-
  Decide quando a pergunta exige o api-sentinel-forge — o observador de
  runtime das APIs: observação de runtime, avaliação de SLO/error budget,
  detecção de anomalia, investigação de incidente e correlação com deploy —
  e como os handoffs reais fluem (`api-sentinel handoff apiforge` emite um
  implementation-request VERIFIED-only; `handoff doctor`/`ingest` com o
  forge-doctor-api). Use para "a API está saudável em produção?", "o último
  deploy regrediu o serviço?", "investigue este incidente 5xx". Não use para
  análise estática (verbos nativos + api-forge-delegate-doctor respondem) nem
  para produzir código/contrato — o sentinel nunca produz e o api-forge nunca
  observa runtime.
compatibility: >-
  Requer `api-sentinel` instalado no ambiente (`api-sentinel doctor`
  verifica workspace/capabilities); perfil `local` é offline-first, perfis
  `aws`/`opentelemetry` degradam para `unavailable:*` sem seus coletores.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

# API Forge — api-sentinel-forge (runtime do serviço)

O api-sentinel é o especialista irmão de **runtime intelligence**: ele
observa telemetria real (métricas, traces, probes, run dumps) e devolve
vereditos honestos — `UNKNOWN`/`UNVERIFIED` são respostas válidas, saúde
fabricada é defeito. O api-forge é estático por contrato: **nunca** infera
latência, TPS, SLO, erro em produção ou causa de incidente sem evidência de
runtime — esse gap é exatamente a fronteira do sentinel.

## Quando o sentinel agrega valor

- **Saúde em runtime** — "a API está saudável agora?", RED/USE, probes —
  o api-forge não tem fatos de runtime; o sentinel sim (ou declara o gap).
- **SLO/error budget** — `api-sentinel slo define|evaluate|list` sobre
  janelas reais; complementa o design de SLI/SLO do
  `api-forge-observability` (design ≠ observação).
- **Incidente** — `api-sentinel investigate`, `incident show|ack|resolve`,
  `hypotheses add|promote|demote|verify` — investigação com hipóteses e
  evidência, não chute.
- **Correlação com deploy** — `api-sentinel changes list|record|import|
  correlate` — "o release X regrediu o serviço?".
- **Verificação independente de runtime** — análise estática do api-forge
  diz o que o código promete; o sentinel diz o que o runtime entregou.
  Divergência vira `unresolved`, não média.

## Quando não usar

- Pergunta estática que os verbos nativos já respondem com evidência
  (`analyze`, `diff contract`, `judge`) — não há fato de runtime a buscar.
- Scan fonte-independent — → `api-forge-delegate-doctor`
  (`apiforge forge doctor`).
- `api-sentinel` ausente do ambiente — reporte o gap (`absent`), instale-o
  via `forge-cli install api-sentinel-forge` ou `pip install
  "api-sentinel-forge>=0.1.0,<0.2.0"`; nunca simule telemetria nem veredito.
- Sem artefatos de runtime — o sentinel recusa honestamente um pedido sem
  telemetria/runs; colete fontes (`api-sentinel sources --register`) antes.

## Como os handoffs fluem (superfícies reais)

1. **Sentinel → API Forge (implementation-request)**: `api-sentinel handoff
   apiforge --incident-id <id> --hypothesis-id <id> --suggested-change "…"`
   — emitido **somente** quando a hipótese está `VERIFIED`; transporte
   ausente é `unavailable` nomeado. O api-forge recebe via a façade
   `apiforge forge` (`forge handoff`, `forge submit` com `origin-engine`,
   task inspect/result) — o sentinel **pede**, o api-forge **implementa**.
2. **Sentinel ↔ Doctor**: `api-sentinel handoff doctor` emite bundle de
   findings; `api-sentinel handoff ingest` re-ingere o veredito do doctor
   como evidência verbatim — separação produtor/verificador preservada.
3. **API Forge → Sentinel**: não existe lane governada de saída; consuma o
   sentinel via seus próprios verbos (`status`, `capabilities`, `slo
   evaluate`, `incident show`, `services`, `workspace`) ou pelo roteamento
   `theforge ask` quando The Forge está no workspace (adapter
   `adapters/apisentinel`, capabilities `api.runtime-observation`,
   `api.slo-assessment`, `api.anomaly-detection`,
   `api.incident-investigation`, `api.deployment-correlation`).

## Procedimento

1. `api-sentinel doctor --json` — workspace, database, capabilities,
   integrations (a ausência é um estado nomeado, não um erro escondido).
2. `api-sentinel capabilities` — o que o perfil instalado realmente oferece.
3. Pergunta de runtime → verbo do domínio (`slo evaluate`, `investigate`,
   `incident show`, `changes correlate`); preserve `UNKNOWN`/`UNVERIFIED`.
4. Achado de runtime que pede mudança de API → `handoff apiforge` (ou o
   humano carrega o request); o api-forge consome, não o contrário.
5. Cite `incident_id`/`hypothesis_id`/veredito verbatim no caso
   `.apiforge/case/`; divergência com findings estáticos vira `unresolved`.

## Recusas e estados a preservar

`absent` (binário/workspace ausente), `unavailable:*` (perfil/coletor sem
pré-requisito), `UNKNOWN`/`UNVERIFIED` (evidência insuficiente),
`refused` (hipótese não-VERIFIED, payload sem fonte). Propague o estado e o
`unlock`, nunca reescreva como sucesso nem como erro genérico — e nunca
preencha com dados de runtime que não existem.
