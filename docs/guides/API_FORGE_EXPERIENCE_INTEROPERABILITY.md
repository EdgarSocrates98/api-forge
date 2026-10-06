# API Forge: experiência e interoperabilidade

Este programa entrega uma superfície terminal unificada sobre os mesmos
serviços de application usados pela CLI/JSON. A TUI é uma projeção: ela não
acessa `RunStore`, `TaskStore`, bancos, hosts ou providers diretamente.

[English version](API_FORGE_EXPERIENCE_INTEROPERABILITY.en.md) · [Distribuição
portátil em português](API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md) · [Portable
distribution in English](API_FORGE_PORTABLE_DISTRIBUTION.md)

## TUI

Instalação opcional:

```bash
python -m pip install -e '.[tui]'
apiforge tui TASK --root .
```

O fluxo inicial é execução. As abas e atalhos cobrem status, doctor, review,
evolve, resume, cancelamento, evidências, capabilities e debate. Em CI ou sem
Textual:

```bash
apiforge tui TASK --root . --fallback
```

O fallback mantém `ExperienceSnapshot` e informa `AF-TUI-UNAVAILABLE` com a
ação segura de instalação. O caminho legado (`apiforge status`, `review`,
`evolve` e `resume`) permanece compatível; o grupo modular é:

```bash
apiforge experience status TASK
apiforge experience doctor TASK
apiforge experience review TASK
```

## Distribuição portátil e contexto

As superfícies novas usam as mesmas facades canônicas para JSON, CLI, MCP e
hosts:

```text
apiforge inspect
apiforge init
apiforge status
apiforge doctor
apiforge workspace status
apiforge context resolve --scope repo
```

O comando separado `apiforge here` não faz parte desta onda: a resolução do
contexto é interna. Sem host, rede ou provider SDK, as capacidades locais
continuam disponíveis. MCP é um processo stdio opcional; a ausência dele não
reduz a capacidade da CLI.

## Evidence Levels

Os contratos de artefato, run, verificação e as novas superfícies carregam
`evidence_level`: `observed`, `declared`, `inferred`, `heuristic`, `verified`
ou `unknown`. Ausência de um campo legado não é sucesso; carrega `unknown`.
Um `verified` deve apontar para receipt/proof independente na camada que o
produziu.

## Knowledge freshness

Packs podem declarar, de forma aditiva, `freshness.window_days`,
`freshness.source_hash` e `freshness.authority`. A fonte externa é sempre uma
observação read-only:

```bash
apiforge knowledge freshness rest-design \
  --receipt .apiforge/source-receipt.json \
  --now 2026-09-23T00:00:00Z
```

`fresh` exige hash compatível e idade dentro da janela. Sem receipt resulta em
`unresolved`; hash divergente ou janela expirada resulta em `stale`. O core não
reescreve o Pack nem faz refresh automático.

## Hosts

Declarações observadas podem ser colocadas em `.apiforge/hosts/*.json` e são
validadas contra `HostDeclaration`. Sem arquivos locais, o resolver usa apenas
o layout estático declarado pelo projeto. A interseção é consultada assim:

```bash
apiforge agentops negotiate --capability mcp
apiforge agentops negotiate --capability subagents --host claude
```

Hosts excluídos e limitações permanecem no payload; a ferramenta nunca
transforma ausência de prova em equivalência entre Codex, Claude, Devin e
Copilot.

Host activation usa templates pertencentes ao pacote, source hashes e preview
com `mutation: none`. Não há overwrite automático de arquivos do usuário;
conflitos exigem aprovação explícita. Symlink, auto-update remoto e paridade
total entre hosts continuam adiados.

## Python matrix

Cada célula precisa de execução observada:

```bash
apiforge migration matrix --ecosystem python \
  --receipt .apiforge/python-3.12.json \
  --receipt .apiforge/python-3.14.json
```

O probe local allowlisted `observe_python_interpreter` registra ambiente,
versão, comando, hash de saída e receipt. Células não executadas ficam
`unresolved`; o resultado local não é claim de CI ou produção.

## Debate adaptativo

`open_adaptive_debate` escolhe um conjunto limitado de participantes, quorum,
rounds e retry budget por risco. O JSON persistido inclui policy, plan,
`replay_id` e dissent. Toda posição precisa de evidência `fact:` e o budget
impede fan-out ilimitado. Providers reais continuam adapters externos; os
gates obrigatórios usam participantes/fakes determinísticos.

## Roteamento adaptativo, scorecards e expertise

As superfícies CLI, MCP, TUI e bridges projetam a mesma decisão e o mesmo
`RoutingPlan/v1`. A run mantém `routing.json` para compatibilidade e grava
`routing-plan.json` com `primary`, `fallbacks`, `parallel`, `reviewers`,
`critic` e `referee`. Isso permite revisar o plano sem depender do host.

O scorecard só é promovido após evidence gate e pode carregar qualidade por
dimensão, custo, duração, tokens e frescor. O corpus adaptativo exige, quando
configurado, `golden`, `holdout`, `mutation` e `adversarial`; sinais observados
precisam de receipts e estados stale/unresolved permanecem não promovidos.

Capabilities podem declarar uma família, uma implementação e expertise packs.
Uma solicitação de família compara implementações elegíveis. Pack ausente gera
`AF-CAPABILITY-ELIGIBILITY` com `field=capability.expertise_packs`; o core não
baixa conhecimento nem altera arquivos do host.

### Extensões A/B/C

O roteamento usa A para risco/complexidade, B para scorecards locais e C para
impacto graph-aware. C acrescenta evidência de impacto, seleção e brief sem
recalcular a avaliação em cada superfície. O artefato canônico é
`graph-impact.json`; `stale`, `missing` e `unresolved` continuam conservadores.
Consulte o [contrato GraphImpactAssessment/v1](../contracts/GraphImpactAssessment-v1.md)
e o [arquivo shipped de C](../../.claude/sdd/archive/GRAPH_AWARE_IMPACT/SHIPPED_2026-09-25.md).

## Gates

```text
ruff check .
mypy src/apiforge
pytest -q
apiforge sdd check --root docs/sdd
python scripts/vendor_caveman.py --check
```

O catálogo de códigos e os estados unresolved estão em
[docs/catalog-contract.md](../catalog-contract.md). A arquitetura e os
critérios completos estão nos artefatos SDD da feature.
