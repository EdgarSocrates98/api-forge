---
name: api-forge-verification
description: >-
  Planeja, executa (via scanners allowlisted) e interpreta a verificação de
  APIs — estratégia de testes, contrato, integração, fuzzing, segurança (OWASP
  API Top 10, BOLA/BFLA, SSRF, secrets, supply chain), resiliência (timeouts,
  retries, circuit breaker, bulkhead, shutdown), chaos, failover e prontidão
  de release. Use para decidir quais testes rodar depois de uma mudança, ler
  relatórios de Semgrep/Trivy/Gitleaks/ZAP/Schemathesis/Pact/coverage, revisar
  segurança de um endpoint, ou quando alguém perguntar "está pronto?", "os
  testes passaram, posso subir?", "is this secure", "what should I test". Não
  use para metas de TPS/latência sob carga (→ api-forge-performance) nem para
  desenhar o contrato (→ api-forge-contract).
compatibility: >-
  Requer o CLI `apiforge`. Execução só de binários allowlisted (`semgrep`,
  `trivy`, `gitleaks`, `k6`) via `apiforge run tool`, sem shell; demais
  ferramentas (pytest, JUnit, Schemathesis, Pact, ZAP, Testcontainers) são
  adapters cujos relatórios são lidos por `apiforge model <tool>`.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — verificação, segurança e resiliência

Exit code zero prova apenas que a ferramenta terminou conforme o próprio
contrato. Não prova cobertura, correção, produção saudável nem ausência de
vulnerabilidade. Esta skill existe para impedir que "verde" vire "pronto"
sem evidência.

## Antes de começar

Siga `api-forge-core`. Derive a estratégia do risco (`apiforge sdd classify`),
do contrato, do `WorkloadProfile` e dos findings — não de uma suíte padrão.

## Procedimento

1. **Plano proporcional ao risco** — nunca a suíte inteira por reflexo:
   ```text
   apiforge verify plan --changed <arquivo> [--changed ...] --risk micro|low|medium|high [--breaking]
   ```
   Retorna o nível V0–V5, só os testes impactados e os comandos.
2. **Cobertura por camada**, proporcional: lint, tipos, unidade, componente,
   integração, contrato, E2E e segurança. Inclua positivos, negativos,
   limites, concorrência, retry, idempotência e autorização por papel.
3. **Segurança** — scanners allowlisted, depois leitura do relatório:
   ```text
   apiforge run tool semgrep --target <dir> --out semgrep.json --config <rules-local>
   apiforge run tool trivy --target <dir> --out trivy.json
   apiforge run tool gitleaks --target <dir> --out gitleaks.json
   apiforge model semgrep|trivy|gitleaks|zap --path <relatório>
   ```
   Use `--dry-run` para mostrar o argv sem executar. Revise por operação:
   authN/authZ, BOLA/BFLA, exposição excessiva de propriedades, validação,
   SSRF, injection, secrets, CORS, TLS, rate limit, logging de dado sensível,
   IAM e dependências.
4. **Contrato e cobertura:** `apiforge model schemathesis|pact|coverage --path <relatório>`.
5. **Resiliência:** `apiforge model resilience --path <dir>` (heurístico,
   pontos cegos nomeados): timeouts coerentes com o SLO, retry com backoff e
   jitter, circuit breaker, bulkhead, pools, graceful shutdown, DLQ.
   Cenários de falha controlada: `apiforge perf chaos` lista CHAOS-001..013 —
   a injeção nunca é executada pelo API Forge.
6. **Falha de teste ou CI:** leia a fatia, não o log inteiro:
   `apiforge slice tests --input <log>` · `apiforge slice log --input <log>`.
7. **Resultado inconclusivo?** `apiforge verify escalate --static <likely|...> --test inconclusive`
   diz o próximo passo; teste conclusivo encerra.
8. **Registre** ferramenta, versão, ambiente, comando, dados, threshold,
   saída e hash; vincule com `apiforge evidence emit` e confira com
   `apiforge evidence verify`.
9. **Verificação independente** para mudanças de segurança, banco,
   infraestrutura e performance: `apiforge task verify` / `task holdout`
   (mutações locais que as provas precisam detectar); o aceitante é
   diferente do executor.

## Estados

`passed`, `failed`, `inconclusive`, `blocked`, `skipped_with_reason`,
`unsafe_to_run`. Nunca colapse `inconclusive` em `passed`, nem `skipped` sem
motivo.

## Guardrails

- Não rode scanner contra alvo remoto sem `--approve` registrado (gate de
  policy `sensitive`).
- Não reporte "sem vulnerabilidades" — reporte "nenhum finding destas
  ferramentas, nesta versão, neste escopo".
- Não use fuzzing, DAST ou chaos contra produção.
- Não desative teste, baixe threshold ou adicione skip para ficar verde.

## Entrega

Plano de verificação (nível + testes), resultados por estado, findings de
segurança com regra e severidade, gaps de resiliência, evidence receipts e
quem verificou de forma independente.

Especialistas típicos: `api-test-strategist`, `api-security-reviewer`,
`api-resilience-engineer`, `api-verifier` (aceitação independente).
