---
name: api-forge-architecture
description: >-
  Escolhe, compara e revisa arquiteturas de API e plataformas de execução a
  partir de um WorkloadProfile declarado — edge (API Gateway, ALB, CloudFront,
  WAF), compute (Lambda, ECS, EKS, EC2), async, dados, identidade,
  multi-região, custo e rollback — e registra a decisão como ADR. Use para
  "Lambda ou ECS?", "como hospedar esta API", planejamento de capacidade
  estrutural, revisão de arquitetura AWS existente a partir de dumps, migração
  de runtime (Spring Boot 2→3, Java/Python/Go), strangler fig ou qualquer
  decisão de deployment. Não use para modelar o acesso a um banco específico
  (→ api-forge-data-access) nem para provar TPS (→ api-forge-performance).
compatibility: >-
  Offline; requer o CLI `apiforge`. Coleta AWS só via família `apiforge
  collect` (opt-in, read-only, gera dumps). Terraform, SAM e AWS CLI são
  adapters opcionais, nunca dependências do core. Para limites e quotas AWS
  atuais, consulte a documentação oficial e cite a data.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — arquitetura e decisão de plataforma

Arquitetura é decisão sob restrição. A plataforma certa sai do perfil de
carga e das restrições declaradas, não da preferência do time nem do que está
na moda. Por isso o primeiro artefato é o `WorkloadProfile`, e a decisão vem
com alternativas rejeitadas e condições de reversão.

## Antes de começar

Siga `api-forge-core`. Separe três colunas desde o início: **fatos
observados** (com `fact_id`), **premissas declaradas** (quem declarou) e
**desconhecidos**. Uma premissa nunca migra para fato sem evidência.

## Procedimento — nova decisão

1. **Construa o `WorkloadProfile`** com todo campo declarado: sync/async,
   burst, latência alvo (p95/p99), TPS de negócio vs RPS, concorrência,
   duração por request, payload, estado, dados, rede/VPC, SLO, RTO/RPO,
   compliance e teto de custo. Campo sem valor fica explícito como
   desconhecido. Schema: `apiforge contract list` / `apiforge contract show <nome>`.
2. **Rode o Architecture Decision Engine:**
   ```text
   apiforge plan architecture --profile workload-profile.json
   ```
   Ele elimina opções por restrição dura, pontua as sobreviventes e emite
   `chosen`, `rejected` com motivo e condições de mudança.
3. **Avalie o conjunto**, não só o compute: edge, compute, dados, eventos,
   identidade, observabilidade, deployment e rollback.
4. **Valide limites AWS** relevantes: quotas, throttling, timeouts,
   concorrência, autoscaling, limites regionais. Cite fonte e data; números
   de memória são hipótese.
5. **Escreva o ADR:** contexto, decisão, alternativas rejeitadas com motivo,
   trade-offs, riscos, evidência e condições que reverteriam a decisão.

## Procedimento — revisão de arquitetura existente

1. Colete postura read-only (opt-in, credencial do host; antes,
   `apiforge evidence gate --question "..."`). Todo collector aceita
   `--out <dump-dir> --now <ISO>` mais o identificador do recurso:
   | Recurso | Identificador |
   |---|---|
   | `collect alb` | `--lb-arn` |
   | `collect ecs` | `--cluster` |
   | `collect eks` | `--cluster-name` |
   | `collect ec2` | `--instance-id` |
   | `collect api-gateway` | `--api-id` |
   | `collect lambda` | `--function-name` |
   | `collect waf` | `--web-acl-id`/`--web-acl-name` + `--scope` |
   | `collect cognito` | `--user-pool-id` |
   | `collect vpc-endpoints` | `--vpc-id` |
2. Modele offline: `apiforge model alb|ecs|eks|ec2|api-gateway|lambda|waf --path <dump>`;
   IaC com `apiforge model terraform --path <dir>` ou `model sam --path <tpl>`.
3. Julgue camada a camada com `apiforge judge --facts <facts.json>` e
   `apiforge rules lookup <id>`; drift entre IaC e dump é finding, não ruído.

## Procedimento — migração e modernização

- Runtime/framework: `apiforge migration analyze <dir> --ecosystem java|python|go --source <v> --target <v>`,
  depois `migration plan`, `migration matrix` (células sem evidência ficam
  `unresolved`) e `migration verify`.
- Strangler fig por rota: `apiforge plan strangler --baseline <legacy-facts.json> --candidate <new-facts.json>`.
- Paridade se prova por diff de contrato e testes, não por declaração.

## Guardrails

- Não escolha EKS por complexidade aspiracional; exija operador, escala ou
  requisito que justifique o custo operacional.
- Não escolha Lambda por custo presumido; custo depende de duração,
  concorrência e tráfego medidos.
- Não confunda RPS do gateway com TPS de negócio.
- Não prometa multi-região sem testar consistência, failover e operação.
- Nenhuma mutação cloud: a decisão é recomendação; aplicar exige identidade,
  conta, região, recurso, impacto, rollback e aprovação humana.

## Entrega

`WorkloadProfile`, matriz de decisão (saída do engine), arquitetura proposta
com diagrama textual, SLOs, riscos, plano de validação (o que
`api-forge-performance` e `api-forge-verification` precisam provar) e ADR.

Especialistas típicos: `api-platform-selector` (decisão nova),
`api-architecture-reviewer` (arquitetura existente), `api-infra-reviewer`
(IaC), `api-modernization-specialist` (migração).
