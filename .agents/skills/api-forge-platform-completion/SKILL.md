---
name: api-forge-platform-completion
description: Audita a prontidão da plataforma API Forge por contracts, capability matrix, cadeia de evidências e seis verticais; use ao validar releases ou adicionar capabilities.
---

# API Forge Platform Completion

Use esta skill quando a tarefa envolve validar a plataforma inteira, adicionar
uma capability pública, revisar uma integração, preparar um agent/skill ou
confirmar prontidão de release. O resultado deve ser uma decisão explicável,
com fatos, premissas, riscos, limitações e um verificador independente.

## Limites obrigatórios

- Leia `AGENT_PROTOCOL.md` e carregue o caso persistido em `.apiforge/case/`
  antes de analisar.
- Quando houver findings, execute `apiforge next-step` antes de escolher um
  especialista ou uma rota.
- Preserve `confirmed`, `unresolved`, `unsupported`, `refused`,
  `not_observed` e `inconclusive` como estados distintos.
- Não transforme parser, fixture, prompt ou plano em prova de runtime.
- Agents devem entender a necessidade, sugerir boas práticas e comparar
  técnicas/arquiteturas; não use wizard obrigatório nem altere escopo, policy
  ou sistema externo por conta própria.
- Toda recomendação deve separar fatos observados, premissas, alternativas,
  trade-offs, riscos, gaps e o próximo verificador.
- Git, CI/CD, cloud, banco, mensageria e vendor são read-only por padrão.
  Qualquer mutação exige adapter, policy, aprovação, rollback e receipt.

## Fluxo mínimo de verificação

1. Confirme o case, seus hashes e o framework detectado.
2. Rode a cadeia `analyze -> next-step -> graph -> evidence -> brief`.
3. Verifique `apiforge capabilities list` e `apiforge capabilities verify`.
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
```

`apiforge capabilities verify` é o gate de documentação, limitações,
verificador e evidência. Se uma command line não aparece no help do CLI, não a
documente como produção; registre-a como proposta ou `unsupported`.

## Estados de capability

| Estado | Uso correto |
|---|---|
| `supported` | O caminho local tem contract, evidência e verificador reproduzíveis. |
| `heuristic` | A projeção estática ajuda, mas não prova comportamento live. |
| `unresolved` | A pergunta é válida, mas faltam evidência ou adapter seguro. |
| `unsupported` | A fronteira atual recusa a operação explicitamente. |

Uma mudança de estado exige atualizar YAML, documentação, verificador, teste e
evidência. Nunca promova uma capability apenas porque apareceu um parser.

## Verticais e surfaces

As seis verticais mínimas são API, database, messaging, CI/CD, cloud e
front-end. Cada uma precisa de uma fixture, um golden e um holdout que preserve
incerteza. As surfaces CLI, MCP, IDE e UI podem mudar a apresentação, mas não
podem mudar estado, gaps, evidência ou semântica de segurança.

Consulte o guia operacional em
`docs/guides/API_FORGE_PLATFORM_USAGE.md`, a matriz em
`docs/capabilities/API_FORGE_CAPABILITY_MATRIX.md` e o contract de saída em
`docs/agents/AGENT_OUTPUT_CONTRACT.md` antes de criar artefatos novos.

## Atualização de mirrors

`.agents/skills` é a fonte canônica. Depois de alterar esta skill, execute:

```text
python scripts/sync_skills.py --root .
apiforge agents sync --root .
```

Valide a skill com `quick_validate.py` quando disponível e rode os gates do
projeto. Não crie uma cópia manual divergente em `.claude`, `.github` ou
`.devin`.
