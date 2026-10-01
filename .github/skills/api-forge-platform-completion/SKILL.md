---
name: api-forge-platform-completion
description: >-
  Audita a prontidão da própria plataforma API Forge — capability matrix,
  estados supported/heuristic/unresolved/unsupported, cadeia analyze →
  next-step → graph → evidence → brief, seis verticais (API, database,
  messaging, CI/CD, cloud, front-end), paridade CLI/MCP/IDE/UI, change-control
  API+Git+CI/CD com `af-change-bundle/1`, receipts externos e probes de
  runtime. Use ao validar uma release do API Forge, adicionar ou promover uma
  capability pública, revisar uma integração, governar uma mudança ligada a
  branch/PR/CI, publicar JUnit/Markdown/SARIF/HTML ou criar/alterar agents e
  skills do projeto. Não use para revisar a API de um cliente (→
  api-forge-core e skills de domínio).
compatibility: >-
  Requer o repositório API Forge, o CLI `apiforge` e Python para `scripts/`.
  GitHub só via adapter GET-only com credencial injetada pelo host; nenhuma
  mutação de Git, CI ou cloud pelo core.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — prontidão da plataforma

Uma capability só é "suportada" quando tem contract, evidência e verificador
reproduzíveis. Esta skill impede que um parser novo, uma fixture ou um plano
sejam promovidos a prova de runtime, e garante que todas as surfaces contem a
mesma verdade.

## Limites obrigatórios

- Leia `AGENT_PROTOCOL.md` e carregue o caso em `.apiforge/case/` antes de
  analisar; com findings, rode `apiforge next-step` antes de escolher rota.
- Preserve `confirmed`, `unresolved`, `unsupported`, `refused`,
  `not_observed` e `inconclusive` como estados distintos.
- Parser, fixture, prompt ou plano não são prova de runtime.
- Agents entendem a necessidade, sugerem boas práticas e comparam técnicas;
  não impõem wizard nem alteram escopo, policy ou sistema externo por conta
  própria.
- Toda recomendação separa fatos, premissas, alternativas, trade-offs,
  riscos, gaps e o próximo verificador (`docs/agents/AGENT_OUTPUT_CONTRACT.md`).
- Git, CI/CD, cloud, banco, mensageria e vendor são read-only por padrão;
  mutação exige adapter, policy, aprovação, rollback e receipt.

## Fluxo mínimo de verificação

1. Confirme o case, seus hashes e o framework detectado.
2. Rode a cadeia `analyze → next-step → graph → evidence → brief`.
3. `apiforge capabilities list` e `apiforge capabilities verify` (gate de
   documentação, limitações, verificador e evidência).
4. Execute os testes da vertical e confirme fixture, golden e holdout.
5. Valide CLI/MCP/IDE/UI pela mesma `CapabilityRequest`/`CapabilityResult`.
6. Registre limitações e evidências no case, na documentação e no Outcome
   Brief. Nunca encerre como `DONE` com gaps obrigatórios.

## Comandos públicos suportados

```text
apiforge capabilities list
apiforge capabilities verify
apiforge analyze --contract <openapi> --project <project> --out-dir <case>
apiforge next-step --findings <case>/findings.json --phase <phase>
apiforge graph build --case <case> --out <graph>
apiforge evidence emit --case <case> --out <receipt.json> --now <ISO8601>
apiforge evidence verify --receipt <receipt.json>
apiforge brief show --task <task-id>
apiforge change-control run --bundle <bundle.json> --out-dir <dir>
apiforge change-control collect --repository <owner/repo> --base-sha <sha> --head-sha <sha>
apiforge change-control verify --run-dir <dir>
apiforge change-control publish --run-dir <dir>
apiforge change-control surface --run-dir <dir> --surface ide|ui --out <file>
apiforge change-control serve --run-dir <dir>
apiforge integration github-issues --repository <owner/repo> --out <receipt.json>
apiforge integration health --url <https-url>/readyz --out <receipt.json>
apiforge integration json --url <https-url>/api/issues --out <receipt.json>
apiforge integration verify-receipt --receipt <receipt.json> --now <ISO8601>
apiforge platform verify-runtime --out <receipt.json>
```

Se uma linha de comando não aparece no `--help` do CLI, não a documente como
produção; registre-a como proposta ou `unsupported`.

## Change control API + Git + CI/CD

- Use `af-change-bundle/1` para mudança ligada a branch, PR ou replay local.
  O bundle é entrada não confiável: é normalizado antes da análise, e a cadeia
  local é `analyze → next-step → graph → evidence → brief → verify → publish`.
- Inspecione `result.json`, `metrics.json` e `brief.json`; freshness do
  provider e segurança de deploy ficam `unresolved` salvo receipt externo
  independente.
- `collect` usa o `GitHubReadOnlyAdapter` (GET-only, transporte injetado) e
  emite bundle sanitizado + `af-change-collection-receipt/1` sem credenciais.
  O receipt não prova autoria, segurança de deploy nem freshness.
- Agents podem recomendar estratégia de merge, política de compatibilidade,
  gates de CI ou arquitetura, mas não fazem merge, push, dispatch, deploy nem
  autofix. A recomendação inclui fatos, premissas, alternativas, riscos,
  unresolved, evidence refs, verificador e confiança.
- `publish` emite JUnit, Markdown, SARIF e HTML standalone; `surface` e
  `serve` expõem o mesmo resultado canônico a IDE/UI sem mudar status ou
  evidência. `serve` aceita loopback local ou deploy remoto autenticado com
  TLS; container e workflow de Pages são surfaces do host, não caminhos de
  mutação do core.
- Leituras externas usam `af-external-read-receipt/1`; probes locais usam
  `af-platform-runtime-receipt/1`. Ambos preservam freshness e limitações em
  vez de transformar prova local em afirmação de produção.
- Toda recusa expõe código `AF-*`, `field` rejeitado e `unlock`; catalogue
  códigos novos em `docs/catalog-contract.md` antes de expô-los.
- O job de CI `open-green-pr` é uma fronteira separada do host: abre ou
  reusa PR só com credencial least-privilege configurada, depois de todos os
  gates. Agents e core nunca fazem essa mutação. `scripts/github_pr_host.py`
  é a única fronteira de mutação GitHub; mudanças de ruleset são planejadas
  com `scripts/github_ruleset_plan.py` (read-only) e aplicadas pelo owner.

## Estados de capability

| Estado | Uso correto |
|---|---|
| `supported` | O caminho local tem contract, evidência e verificador reproduzíveis. |
| `heuristic` | A projeção estática ajuda, mas não prova comportamento live. |
| `unresolved` | A pergunta é válida, mas faltam evidência ou adapter seguro. |
| `unsupported` | A fronteira atual recusa a operação explicitamente. |

Mudar estado exige atualizar YAML, documentação, verificador, teste e
evidência. Nunca promova uma capability só porque apareceu um parser.

## Verticais e surfaces

As seis verticais mínimas são API, database, messaging, CI/CD, cloud e
front-end. Cada uma precisa de fixture, golden e holdout que preserve
incerteza. CLI, MCP, IDE e UI podem mudar a apresentação, mas não estado,
gaps, evidência ou semântica de segurança.

Referências antes de criar artefatos novos:
`docs/guides/API_FORGE_PLATFORM_USAGE.md`,
`docs/capabilities/API_FORGE_CAPABILITY_MATRIX.md`,
`docs/agents/AGENT_OUTPUT_CONTRACT.md`.

## Agents e skills do projeto

- **Agents:** edite só `agents/*.md`, depois `apiforge agents sync` e
  `apiforge agents lint` (e `agents check`); os mirrors em `.claude/agents`,
  `.agents/agents` e `.codex/agents` são gerados.
- **Skills:** `.agents/skills` é a fonte canônica. Depois de alterar uma
  skill:
  ```text
  python scripts/validate_skills.py
  python scripts/sync_skills.py --root .
  python scripts/validate_skills.py --check-mirrors
  ```
  Não edite `.claude/skills`, `.github/skills` nem `.devin/skills` à mão —
  o sync sobrescreve e a edição se perde.
