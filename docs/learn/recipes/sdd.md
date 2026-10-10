# Receita — conduzir uma mudança pelo SDD do API Forge

**O quê:** o fluxo Spec-Driven Development: `sdd classify` nomeia o
perfil mínimo de risco; as fases `discover → intent → contract →
architecture → plan → build → verify → secure → benchmark → ship`
avançam por gates de evidência com cascata de hashes.
**Por que:** mudança estrutural sem SDD é onde entram regressões
silenciosas — cada fase tem um artefato e um gate.
**Quando:** feature nova, mudança de contrato, migração, mudança de
banco, segurança ou infra.
**Quando não:** revisão de um endpoint isolado sem mudança planejada —
aí é a skill do domínio direto.

## Problema

"Vou mudar o contrato e o acesso a dados — por onde começo?"

## Pré-requisitos

`apiforge` instalado; a skill `api-forge-sdd` carregada no host (ela
conduz o fluxo e os gates).

## Passo a passo

```bash
apiforge sdd classify --change "mudança de contrato + data access"
apiforge sdd status --root .
apiforge sdd check --feature <feature> --phase contract
apiforge sdd stamp --file docs/sdd/<feature>/contract.md
```

No host: "use a skill `api-forge-sdd` para conduzir esta feature".

## Saída esperada / interpretação

`classify` devolve o perfil mínimo (micro/quick/standard/critical/
migration) com a justificativa determinística; `check` valida a cascata
de hashes e os metadados de fase — `refused` quando a evidência não
sustenta o avanço.

## Verificação

`sdd check` recusar é o gate funcionando — o unlock vem nomeado na
recusa; pular fase exige evidência explícita, nunca declaração.

## Limitações

O SDD governa o processo, não prova correção — `verify`/`benchmark` são
fases com evidência própria.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `check` recusa | artefato sem `stamp` ou fase sem evidência | leia o `rejected field` |
| perfil alto demais | mudança simples | `classify` é a fonte — não escolha a olho |

## Uso por agentes

A skill `api-forge-sdd` é o condutor — a CLI valida, nunca decide sozinha.
