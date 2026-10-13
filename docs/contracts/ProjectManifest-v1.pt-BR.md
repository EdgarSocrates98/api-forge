# ProjectManifest-v1 (PT-BR)

Manifesto mínimo que conecta um repositório consumidor ao API Forge sem copiar
o pacote para dentro dele.

[English](ProjectManifest-v1.md) · [Guia portátil](../guides/API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md)

## Campos

| Campo | Tipo | Uso |
|---|---|---|
| `schema` | `apiforge/project/v1` | Identidade fechada do contrato |
| `version` | `1` | Versão do contrato |
| `project_id` | string | Identidade estável do projeto |
| `root` | path absoluto | Raiz do repositório/projeto |
| `workspace_id` | string opcional | Workspace virtual declarado |
| `default_scope` | `repo\|workspace\|target` | Escopo padrão de contexto |
| `target` | string opcional | Alvo padrão quando declarado |
| `hosts` | lista de strings | Hosts explicitamente conectados |
| `evidence_refs` | lista de strings | Referências de evidência |

O manifesto não aceita secrets, credenciais, prompts, knowledge packs ou
arquivos de host. `hosts` e `evidence_refs` são normalizados e ordenados.

## Inicialização

```text
apiforge init
```

O comando cria somente `.apiforge/project.yaml` e informa a mutação local
mínima.
