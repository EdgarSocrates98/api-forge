---
name: api-forge-delegate-doctor
description: >-
  Decide quando delegar um scan independente ao forge-doctor-api pela lane
  governada `apiforge forge doctor` — drift de contrato, breaking change,
  migração, revisão de segurança/política ou verificação independente de um
  achado — e como consumir o registro `apiforge/doctor-delegation/v1`,
  inclusive linhas `UNKNOWN` e recusas `AF-DELEG-*`. Use para "rodar o
  doctor", "compare antes/depois", "o doctor achou o quê?". Não use para o
  health-check da instalação (→ `apiforge doctor`) nem para análise que os
  verbos nativos já respondem com evidência.
compatibility: >-
  Requer `forge-doctor-api` instalado ou no PATH para `scan`; `discover`,
  `list` e `show` funcionam sem ele. A lane é read-only e nunca muta o
  projeto escaneado.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

# API Forge — delegação ao forge-doctor-api

O doctor é um especialista irmão que varre um projeto de API e devolve
findings com severidade e confiança **declaradas por ele**, ecoadas verbatim.
A lane `apiforge forge doctor` é evidence-collection only: nenhum caminho
muta o projeto, e toda recusa persiste um registro `refused`/`failed` antes
de falhar.

## Quando o doctor agrega valor

- **Drift de contrato** — suspeita de que o serviço publicado diverge do
  contrato/código e uma segunda leitura independente confirma ou refuta.
- **Breaking change / migração** — antes e depois de uma mudança arriscada:
  `forge doctor scan` em cada estado, `forge doctor compare` nos run ids
  persistidos; o diff é a evidência de revalidação.
- **Revisão independente** — security/policy/breaking como gate:
  `--fail-on breaking,security,policy` faz o doctor vetar a categoria
  declarada.
- **Achado `unresolved`** — quando os verbos nativos deixaram um gap que um
  scan externo do mesmo alvo pode fechar.

## Quando não delegar

- Verbo nativo já respondeu com evidência (`diff contract`, `judge`,
  `contract-intel impact`) — delegar não adiciona fato.
- `forge doctor discover` retornou `absent` — instale `forge-doctor-api` ou
  siga com análise nativa; nunca simule a execução.
- `untrusted` — `--version` não respondeu `forge-doctor-api <semver>`;
  `--allow-unverified` é decisão explícita do operador, não do agente.
- A pergunta pede mutação ou plan/implement — o doctor só diagnostica.

## Procedimento

1. `apiforge forge doctor discover` — `absent | untrusted | verified`.
2. `apiforge forge doctor scan --target <dir> [--fail-on ...]
   [--correlation-id <id>]` — argv-only governado, env com credenciais
   removidas, timeout e cap de saída (8 MiB; exceder é `AF-DELEG-OUTPUT-LIMIT`,
   nunca truncamento silencioso).
3. Consuma o registro `apiforge/doctor-delegation/v1` em
   `.apiforge/forge/delegations/<run_id>/` (`forge doctor list`,
   `forge doctor show <run_id>`). Linhas `UNKNOWN|subject|missing` são
   evidência de gap — preserve-as; nunca as promova a confirmed nem as
   descarte.
4. `apiforge forge doctor compare --baseline <run> --current <run>` —
   revalidação before/after; só prova mudança quando os dois runs existem.
5. Cite `run_id`, severidade e confiança do doctor verbatim; divergência com
   findings nativos vira `unresolved`, não média.

## Recusas a preservar

`AF-DELEG-*` são estados nomeados com `unlock`, não falhas genéricas:
`ABSENT` (instale o doctor), `INCOMPATIBLE` (versão/schema), `TARGET`,
`POLICY` (gate de policy), `READ-ONLY` (argv fora do template — a lane
nunca muta), `TIMEOUT`, `USAGE`, `FAILED`, `INVALID-OUTPUT`,
`OUTPUT-LIMIT`, `CYCLE` (provider em `visited_providers`), `BUDGET` (hops
ou tempo do chain esgotado), `CANCELLED`, `RUN-ID`, `EXISTS`, `NOT-FOUND`,
`STORE`. Propague o código e o `unlock`, nunca os reescreva como erro de
serviço.
