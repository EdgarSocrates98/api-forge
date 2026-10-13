# Economia de contexto — referência

Carregue este arquivo quando precisar verificar, buscar, citar ou mudar
política econômica. O fluxo básico (capsule, delta, handoff) está no
`SKILL.md`. Guia completo: `docs/guides/API_FORGE_ECONOMY.md`.

## Sumário

- Verificar, buscar e citar com economia
- Saída e ferramentas econômicas
- Evidência honesta de economia
- Mudar política econômica

## Verificar, buscar e citar com economia

- Depois de mudar arquivos: `apiforge verify plan --changed <arquivo> --risk <micro|low|medium|high>`
  dá o nível V0–V5 e só os testes impactados; não rode a suíte inteira salvo V5.
- Conhecimento: `apiforge knowledge search --query "..."` devolve 3 trechos
  ranqueados; peça `--tier 2` só se não bastar.
- Evidência: `apiforge evidence resolve evidence://finding/<id>` traz um salto
  por vez; siga os `neighbors` sob demanda.
- `apiforge economy doctor` aponta configurações que encarecem runs;
  `apiforge economy tier` só barateia modelo com benchmark.
- Antes de consultar AWS/Datadog/CloudWatch/GitHub:
  `apiforge evidence gate --question "..."`; pergunta estática fica no
  OpenAPI/código local, só pergunta de efeito em runtime ganha
  `live_read_only` (nunca mutação).
- Teste inconclusivo? `apiforge verify escalate --static likely --test inconclusive`
  diz o próximo passo; teste conclusivo encerra.
- Knowledge vencido: `apiforge knowledge watch --manifest <upstream.json> --now <iso>`
  lista só os packs `refresh_needed`; o refresh é outro workflow.
- Ao retomar: `apiforge runtime checkpoint <task> <run>` mostra o gasto já
  feito; o resume nunca baixa o perfil. Orçamento por fase SDD:
  `apiforge economy phase-budget --profile <p>`.

## Saída e ferramentas econômicas

- Pergunta sobre artefato → verbo do Forge antes de ler arquivos
  (`apiforge agentops projection --host <host>` lista o `verb_map`).
- `apiforge --output compact <verbo>` (ou `APIFORGE_OUTPUT=compact`) remove
  só null/vazio, sem perda.
- Artefato de comando grande: `apiforge context compact` mantém linhas
  críticas e aponta para o artefato completo.
- Falha de teste ou CI: `apiforge slice tests --input <log>` /
  `apiforge slice log --input <log>`; expanda o `log_ref` só se precisar.
- MCP compacto: `apiforge-mcp --surface compact` expõe 6 gateways; ache a
  ferramenta com `apiforge_discover` e execute com `apiforge_call`.

## Evidência honesta de economia

- `apiforge economy stats --run-id <id>` mostra bytes por fonte e
  `token_coverage`; tokens só existem com transcript
  (`economy stats --transcript`) — bytes não são tokens.
- `apiforge economy explain <run_id>` diz por que cada ref foi gasta.
- `apiforge economy roi` mostra se agentes extras mudam o resultado.
- `apiforge evals agentic-quality` gradua vereditos gravados com piso
  `--min-accuracy` e `--baseline`; `apiforge evals economy-hardening` roda o
  código de produção.
- Paths de case, fact ou `--changed`/`--case-dir` fora do projeto viram
  `AF-PATH-OUTSIDE-ROOT` e nunca são lidos.

## Mudar política econômica

Budgets nunca cortam contract, verify, secure, provenance nem o relato de
`unresolved`.

1. `apiforge evals economy-matrix --out antes.json`
2. aplique a mudança de perfil, roteamento ou corte;
3. `apiforge evals economy-matrix --out depois.json`
4. `apiforge evals gate --baseline antes.json --candidate depois.json` — só
   siga com `ship`.
5. `apiforge evals replay --corpus evals/corpus/economy-replay` mostra o
   efeito em runs guardados sem chamar provedor.
6. Antes de entregar: `apiforge evals economy-hardening` e
   `apiforge evals agentic-quality --baseline <relatório anterior>`.
