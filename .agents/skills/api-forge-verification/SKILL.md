---
name: api-forge-verification
description: Planeja e verifica testes de APIs, segurança, contratos, resiliência, integração, fuzzing, chaos, failover e release readiness. Use para decidir quais testes executar, interpretar resultados e impedir conclusões baseadas apenas em exit code verde.
compatibility: Ferramentas como pytest, JUnit, REST Assured, Testcontainers, Schemathesis, Pact, ZAP, Semgrep, Trivy, Gitleaks e Fault Injection são adapters opcionais.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Derive a estratégia do risco, contrato, WorkloadProfile e findings.
2. Cubra lint, tipos, unidade, componente, integração, contrato, E2E e segurança proporcionalmente.
3. Inclua casos positivos, negativos, limites, concorrência, retry, idempotência e autorização.
4. Para sistemas distribuídos, planeje timeout, retry, circuit breaker, bulkhead, fila, DLQ, shutdown e recovery.
5. Para cada teste, registre ferramenta, versão, ambiente, comando, dados, threshold, saída e hash.
6. Classifique como `passed`, `failed`, `inconclusive`, `blocked`, `skipped_with_reason` ou `unsafe_to_run`.
7. Exija verificação independente para mudanças de segurança, banco, infraestrutura e performance.

## Segurança

Verifique authN/authZ por operação, BOLA/BFLA, exposição excessiva, validação, SSRF, injection, secrets, CORS, TLS, rate limit, logging, IAM e supply chain.

## Regra de aceitação

Exit code zero prova apenas que a ferramenta terminou conforme seu contrato. Não prova cobertura, correção, produção saudável ou ausência de vulnerabilidade.

