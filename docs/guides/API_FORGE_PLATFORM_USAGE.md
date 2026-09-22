# API Forge Platform Usage

Este guia descreve o uso público da fundação de completude da API Forge. Ele
é válido para CLI, MCP, bridges de IDE e projeções de UI porque essas surfaces
compartilham `CapabilityRequest/v1` e `CapabilityResult/v1`.

## 1. Princípio operacional

API Forge é um control plane determinístico, offline-first e evidence-first.
Ele observa artefatos, constrói IRs e facts, recomenda técnicas e arquiteturas
e produz planos verificáveis. Não presume que um parser provou runtime, que um
golden provou produção ou que uma integração nominal tem permissão para mutar.

Agents devem entender a necessidade antes de recomendar. A resposta deve
separar observações, premissas, alternativas, trade-offs, riscos, limitações,
gaps e o próximo verificador. Não há wizard obrigatório: a adaptação acontece
por contexto, contratos e evidências.

Antes de uma análise:

```text
1. Leia AGENT_PROTOCOL.md.
2. Carregue ou crie um case em .apiforge/case/.
3. Se houver findings, rode apiforge next-step antes de escolher especialista.
4. Preserve todos os diagnósticos e hashes.
```

## 2. Instalação e primeiro diagnóstico

```bash
python -m pip install -e '.[dev]'
apiforge capabilities list
apiforge capabilities verify
apiforge analyze \
  --contract tests/fixtures/openapi/orders-v1.yaml \
  --project tests/fixtures/fastapi_orders \
  --out-dir .apiforge/case
```

`capabilities verify` deve retornar `ok: true`. Se uma capability aparecer
como `heuristic`, `unresolved` ou `unsupported`, esse estado é a conclusão
correta até que sua evidência e verificador sejam adicionados.

## 3. Cadeia crítica completa

O fluxo mínimo de prova é:

```text
analyze → next-step → graph → evidence → brief
```

Exemplo usando os artefatos oficiais:

```bash
apiforge next-step \
  --findings .apiforge/case/findings.json \
  --phase verify

apiforge graph build \
  --case .apiforge/case \
  --out .apiforge/graph

apiforge evidence emit \
  --case .apiforge/case \
  --out .apiforge/evidence/receipt.json \
  --now 2026-09-22T00:00:00Z

apiforge evidence verify \
  --receipt .apiforge/evidence/receipt.json

apiforge task create platform-review \
  --outcome "revisar a prontidão da plataforma" \
  --root .apiforge
apiforge brief show --task platform-review --root .apiforge
```

`brief show` pode terminar em `REVIEW`, `DECIDE` ou `BLOCKED`. Isso é uma
decisão governada, não uma falha do pipeline. `DONE` só é aceitável quando a
evidência independente, o receipt, os hashes, os holdouts e os gaps obrigatórios
estão resolvidos.

## 4. Capability matrix

A fonte é `src/apiforge/rules/capability_matrix.yaml` e a explicação humana é
`docs/capabilities/API_FORGE_CAPABILITY_MATRIX.md`.

| Estado | Interpretação | Próximo passo |
|---|---|---|
| `supported` | Existe caminho local reproduzível com contract, evidence e verifier. | Reexecutar o verifier quando os inputs mudarem. |
| `heuristic` | Há orientação determinística a partir de sinais estáticos/declarados. | Coletar evidência de runtime antes de declarar suporte. |
| `unresolved` | A pergunta é válida, mas falta evidência ou adapter seguro. | Nomear o gap e solicitar contexto/evidência. |
| `unsupported` | A operação é recusada pela fronteira atual. | Criar design e policy explícitos antes de implementar. |

Toda capability pública precisa declarar documentação, limitações, evidências,
pré-requisitos, risco, rollback e verificador. O gate é:

```bash
apiforge capabilities verify
```

## 5. Verticais e projetos de exemplo

Cada vertical possui uma célula de prova em `tests/fixtures/platform/`:

| Vertical | Fixture | Golden | Holdout |
|---|---|---|---|
| API | `api/openapi.yaml`, `api/app.py` | `api/golden.json` | `api/holdout.yaml` |
| Database | `database/schema.sql`, `database/repository.py` | `database/golden.json` | `database/holdout.yaml` |
| Messaging | `messaging/asyncapi.yaml`, `messaging/consumer.py` | `messaging/golden.json` | `messaging/holdout.yaml` |
| CI/CD | `cicd/pipeline.yaml` | `cicd/golden.json` | `cicd/holdout.yaml` |
| Cloud | `cloud/main.tf` | `cloud/golden.json` | `cloud/holdout.yaml` |
| Front-end | `frontend/package.json`, `frontend/src/api.ts` | `frontend/golden.json` | `frontend/holdout.yaml` |

Valide a matriz com:

```bash
python -m pytest -q tests/labs/test_platform_verticals.py
```

Fixture é exemplo; golden é expectativa revisada; holdout é o caminho de
incerteza/ausência/negativo. Nenhum deles prova custo, throughput, lag,
permissão, índice, browser behavior ou garantia de entrega em produção.

## 6. Agents e recomendações

O agent `api-platform-completion-reviewer` revisa:

- estado, limites, docs e verifier de cada capability;
- fixture/golden/holdout das seis verticais;
- paridade CLI/MCP/IDE/UI;
- evidências independentes e bloqueios de mutação;
- recomendação arquitetural baseada na necessidade e restrições declaradas.

O output deve seguir `docs/agents/AGENT_OUTPUT_CONTRACT.md`, com no mínimo:
`recommendation`, `facts`, `assumptions`, `alternatives`, `risks`,
`unresolved`, `evidence_refs`, `verifier` e `confidence`. O supervisor rejeita
payload incompleto e mantém os gaps visíveis.

## 7. Git, CI/CD, IDE, UI e integrações

As integrações locais em `src/apiforge/integrations/` oferecem uma boundary
estática/read-only. Elas podem inspecionar contexto, montar plano e nomear
requisitos; não devem publicar, executar SQL, alterar pipeline, fazer deploy,
commitar, enviar mensagens ou mudar topology.

Uma ação `apply` só pode avançar quando houver adapter explícito, policy
allowlist, identidade/credencial, aprovação humana, rollback e receipt. Sem
isso, o resultado correto é `blocked`, `unresolved` ou `unsupported`.

CLI, MCP, IDE e UI devem projetar o mesmo resultado canônico. A apresentação
pode mudar; estado, evidência, gaps e semântica de segurança não.

## 8. Verificação antes de commit/release

```bash
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src/apiforge
python -m pytest -q
python scripts/check_release.py
apiforge agents check --root .
apiforge capabilities verify
```

Para alterações em skill ou agent, sincronize os mirrors antes dos gates:

```bash
python scripts/sync_skills.py --root .
apiforge agents sync --root .
```

## 9. Limitações públicas

O estado atual não declara como produção: providers live específicos, um
protocolo IDE implantado, uma UI distribuída, execução de scanners ausentes,
benchmarks de produção ou mutações externas. Esses limites permanecem na
matriz para evitar promessas sem evidência. A evolução correta é adicionar um
adapter read-only, contract, fixture/golden/holdout, verifier, documentação e
policy de rollback antes de promover o estado.
