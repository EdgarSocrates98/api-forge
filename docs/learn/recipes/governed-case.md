# Receita — trabalho governado com evidência persistida

**O quê:** o case `.apiforge/case/` + `next-step` + `evidence`/`brief` — o
ciclo `analyze → next-step → graph → evidence → brief` do AGENTS.md.
**Por que:** decisões com hash e provenance, não memória de chat.
**Quando:** qualquer trabalho não-trivial; exigido pelo operating contract.
**Quando não:** one-off read-only trivial (`apiforge doctor`, `--help`).

## Problema

"Quero auditar depois o que o agente decidiu e por quê."

## Passo a passo

```bash
apiforge analyze --contract api/openapi.yaml --project .
apiforge next-step            # especialista determinístico p/ os findings
apiforge evidence gate        # antes de qualquer fonte viva
apiforge brief                # outcome brief com gaps não resolvidos
```

## Saída esperada / interpretação

`next-step` escolhe o especialista *dos findings* — nunca chute. `brief`
fecha com unresolved declarado; `DONE` sem verificação independente é
proibido pelo contrato.

## Verificação

`.apiforge/case/` contém os artefatos com hashes; `apiforge context capsule`
resume sem abrir o case inteiro (economia).

## Limitações

O case persiste evidência — não executa cloud nem aprova nada; mutações
ficam em sandbox com policy gate explícito.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `AF-PATH-OUTSIDE-ROOT` | path fora do projeto | paths só dentro do root |
| next-step vazio | nenhum finding no case | rode `analyze` antes |

## Uso por agentes

Este é O fluxo do host: `discover → … → verify → ship` do SDD. Skills do
Devin: `.devin/skills/api-forge-devin-runbook`.
