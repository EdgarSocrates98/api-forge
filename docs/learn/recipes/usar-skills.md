# Receita — usar as 14 skills canônicas do API Forge

**O quê:** as skills `api-forge-*` — o conhecimento de procedimento que
o host carrega por gatilho (contrato, descoberta, dados, mensageria,
streaming, observabilidade, performance, SDD, contexto, grafo,
verificação, plataforma).
**Por que:** a skill é o "como fazer" versionado — o agente sem ela
reinventa procedimento e inventa capacidade.
**Quando:** o gatilho da skill aparece na tarefa ("é breaking?",
"mapeie essa API", "aguenta 500 TPS?").
**Quando não:** o gatilho é de outra skill — cada SKILL.md declara
"Não use para…" e o destino certo.

## Problema

"Preciso revisar se essa mudança quebra consumidores — qual skill?"

## Pré-requisitos

Install com skills (qualquer perfil); os mirrors canônicos ficam em
`.github/skills` e replicam para `.claude/skills`, `.agents/skills`,
`.devin/skills`.

## Passo a passo

```bash
ls .claude/skills/           # 14 skills instaladas no projeto
apiforge next-step           # ou deixe o roteador escolher a skill
```

No host: "use a skill `api-forge-contract` neste openapi.yaml".

## Saída esperada / interpretação

Cada SKILL.md abre com gatilhos, o procedimento ordenado e o
"Não use para…" — o host carrega a certa pelo pedido, não por lista.

## Verificação

`validate_skills.py` (scripts/) valida frontmatter e estrutura; o
inventário canônico é `.github/skills` — mirrors divergentes são
regenerados pelo install/sync.

## Limitações

Skills são procedimento, não execução — a skill diz o que rodar; o CLI/
MCP executa deterministicamente.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| skill errada carrega | gatilho ambíguo | o "Não use para" do SKILL.md desambigua |
| 13 em vez de 14 | `_shared`/fragmentos | só diretórios com SKILL.md contam |

## Uso por agentes

`api-forge-core` é o ponto de entrada: tarefa ainda sem área clara passa
por ela, que roteia para a skill específica.
