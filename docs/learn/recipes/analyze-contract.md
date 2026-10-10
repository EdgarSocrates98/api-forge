# Receita — o código implementa o contrato OpenAPI?

**O quê:** `apiforge analyze` cruza um documento OpenAPI com o projeto que o
implementa, determinístico e offline, e persiste um case.
**Por que:** drift contrato↔código é a fonte nº 1 de quebra silenciosa.
**Quando:** review de API, pré-merge, auditoria de implementação.
**Quando não:** validação de runtime/comportamento vivo — analyze é estático;
runtime vai para `apiforge runtime` com evidência exportada.

## Problema

"Meu FastAPI diz servir o `openapi.yaml`, mas será?"

## Pré-requisitos

`apiforge` instalado; um `openapi.yaml` + o root do projeto (FastAPI/Spring/Go
— `--framework auto` detecta).

## Passo a passo

```bash
apiforge analyze --contract api/openapi.yaml --project . \
  --fail-on high          # exit 4 se findings >= high
apiforge next-step        # o que fazer com os findings do case
```

## Saída esperada / interpretação

Findings com severidade + refs em `.apiforge/case/` (preservados com hashes;
a saída compacta é projeção, nunca fonte). Exit code: 0 ok, 4 gate
`--fail-on`, envelope `{error, exit_code}` em recusa.

## Verificação

`apiforge next-step` deve listar os findings persistidos — se o case sumiu,
o analyze não persistiu (verifique `--out-dir`).

## Limitações

Sem execução de código, sem chamadas de rede, sem LLM: é análise estática
declarativa; `--baseline` cobre diff, não cobertura de testes.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `AF-*` refusal com `unlock` | campo rejeitado pela política | leia `rejected field` + `unlock` na saída |
| framework errado | `--framework auto` falhou no layout | force `--framework fastapi` |
| case vazio | `--out-dir` fora do esperado | aponte `.apiforge` |

## Uso por agentes

Contrato de entrada do host: analyze → next-step → evidence → brief.
`--json` estruturado; refusal sempre carrega código `AF-*`.
