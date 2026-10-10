# Receita — o que quebrou entre duas versões da API?

**O quê:** `apiforge analyze --baseline` (e `contract` verbs) emitem diff de
contrato tipado — não diff de texto.
**Por que:** "removeu endpoint" precisa ser evento classificado, não hunk.
**Quando:** versionamento de API, revisão de PR, release notes.
**Quando não:** diff de implementação — isto é contrato, não código.

## Problema

"De `v1` para `v2` do `openapi.yaml`, o que é breaking?"

## Passo a passo

```bash
apiforge analyze --contract api/openapi-v2.yaml --project . \
  --baseline api/openapi-v1.yaml
```

## Saída esperada / interpretação

Eventos de mudança classificados (breaking vs não-breaking) ancorados no
case — com o `--fail-on` você transforma em gate de CI.

## Verificação

O case em `.apiforge/case/` lista os eventos; re-rodar com os mesmos inputs
produz a mesma classificação (determinístico).

## Limitações

Diff semântico de contrato — renomear schema pode aparecer como remove+add
dependendo do nível de evidência; não infere compatibilidade de runtime.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| baseline ignorado | caminho inválido | o erro vem no envelope com `exit_code` |
| breaking falso-positivo | regra estrita | `--fail-on` tolera, findings continuam |

## Uso por agentes

Ideal em pipelines: `--json` + `--fail-on` vira gate; o agente lê os eventos
tipados em vez de parsear texto.
