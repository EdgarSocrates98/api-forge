# Catálogo de payloads Devin

Idioma: [English](README.md) · [Português (Brasil)](README.pt-BR.md)

Gere cada payload a partir da raiz do repositório. O comando emite o JSON
completo `DevinPayload/v1`; mantenha a saída como artefato local quando um
transcript ou registro de revisão for necessário.

## 1. Discovery somente leitura na CLI

```text
apiforge devin payload "Discover the next API Forge improvement from the persisted case" --surface cli --task-kind discovery --detail-level full
```

Use `/plan` e inspecione o routing proposto antes de permitir edições.

## 2. Implementação no Desktop

```text
apiforge devin payload "Implement the approved change with tests and docs" --surface desktop --task-kind implementation --permission-mode normal --detail-level full
```

Cole o `prompt` gerado no Agent Command Center do Devin Desktop e revise o
diff antes de aceitar mudanças de arquivo.

## 3. Verificação/revisão na CLI

```text
apiforge devin payload "Review the current diff and report evidence-backed gaps" --surface cli --task-kind review --detail-level full
```

Execute com permissões normais. Um reviewer pode usar o subagent
`api-forge-reviewer`, mas o resultado do subagent não é verificação
independente até que checks e evidências do API Forge sejam registrados.

## 4. Handoff explícito para Cloud

```text
apiforge devin payload "Continue the approved task in Devin Cloud" --surface cloud --task-kind handoff --detail-level full
```

Use `/handoff` somente depois de confirmar repositório, plataforma, branch e
limites de aprovação humana. Retorne com `/pickup` e execute novamente a
verificação local.
