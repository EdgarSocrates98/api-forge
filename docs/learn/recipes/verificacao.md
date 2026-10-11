# Receita — decidir o que testar antes de declarar pronto

**O quê:** `apiforge verify plan` devolve a escada de verificação para o
risco — os testes impactados e os comandos para rodá-los —
`verify escalate` dá o próximo passo (static → test → stop; runtime
read-only só se inconclusivo).
**Por que:** "os testes passaram" não é verificação — o plano nomeia o
que o risco exige, e a escalada é honesta sobre quando parar.
**Quando:** depois de uma mudança, antes de declarar `DONE` ou abrir PR.
**Quando não:** metas de TPS/latência — aí é `apiforge-performance`;
desenhar timeouts/retries — `api-forge-verification` como skill.

## Problema

"Mudei o handler — o que preciso rodar antes de dizer que está pronto?"

## Pré-requisitos

Um caso/task com a mudança; o plano lê o impacto real, não uma lista
genérica.

## Passo a passo

```bash
apiforge verify plan --task <task_id>        # ou --risk high
apiforge verify escalate --task <task_id>    # próximo passo honesto
```

## Saída esperada / interpretação

`plan`: o nível da escada + testes impactados + comandos. `escalate`:
o próximo passo com `stop` quando a evidência já basta — runtime
read-only aparece só se a verificação ficar inconclusiva.

## Verificação

O plano nunca executa — ele nomeia comandos; quem roda é você ou o host.
Saída sem comando para um risco alto é `unresolved`, não silêncio.

## Limitações

Sem execução: `verify` planeja; os resultados entram como evidência de
case. Runtime probes ficam atrás de `platform verify-runtime` (opt-in,
allowlisted, fixtures).

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| plano genérico | task sem impacto mapeado | `graph build`/`analyze` primeiro |
| `escalate` para cedo | evidência inconclusiva | o passo retornado é o mínimo honesto |

## Uso por agentes

A skill `api-forge-verification` conduz a estratégia completa —
contrato, integração, fuzzing, segurança, resiliência — com `verify`
como o verbo executável.
