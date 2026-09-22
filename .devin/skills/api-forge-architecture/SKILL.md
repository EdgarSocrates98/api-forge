---
name: api-forge-architecture
description: Escolhe e compara arquiteturas de APIs e plataformas de execução. Use para planejamento, workload profile, Lambda, ECS, EKS, EC2, API Gateway, ALB, CloudFront, WAF, MSK, filas, multi-região, custo, segurança, escalabilidade ou decisões de deployment.
compatibility: Para AWS atualizada, consulte documentação oficial; Terraform, SAM e AWS CLI são adapters opcionais e não devem ser dependências do core.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Construa um `WorkloadProfile`: sync/async, burst, latência, TPS, RPS, concorrência, duração, payload, estado, dados, rede, SLO, RTO/RPO e custo.
2. Separe fatos observados de premissas declaradas e desconhecidos.
3. Compare alternativas: serverless, containers gerenciados, Kubernetes, VM, streaming e mensageria.
4. Avalie edge, compute, data, eventos, identidade, observabilidade, deployment e rollback como um conjunto.
5. Para AWS, valide quotas, throttling, timeout, concorrência, autoscaling, limites regionais e disponibilidade.
6. Produza decisão, alternativas rejeitadas, trade-offs, riscos, evidência e condições de reversão.

## Guardrails

- não escolha EKS por complexidade aspiracional;
- não escolha Lambda por custo presumido;
- não confunda RPS do gateway com TPS de negócio;
- não prometa multi-região sem testar consistência, failover e operação;
- não permita mutação cloud sem identidade, conta, região, recurso, impacto e rollback.

## Entrega

Entregue `WorkloadProfile`, matriz de decisão, arquitetura proposta, diagrama textual, SLOs, riscos, plano de validação e ADR.

