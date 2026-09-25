# WorkspaceManifest-v1 (PT-BR)

Manifesto de um workspace virtual composto por repositórios independentes.

[English](WorkspaceManifest-v1.md) · [Guia portátil](../guides/API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md)

## Campos

| Campo | Tipo | Uso |
|---|---|---|
| `schema` | `apiforge/workspace/v1` | Identidade fechada do contrato |
| `version` | `1` | Versão do contrato |
| `workspace_id` | string | Identidade estável do workspace |
| `name` | string | Nome humano do workspace |
| `root` | path absoluto | Diretório do workspace virtual |
| `repositories` | lista de `RepositoryRef` | Raízes independentes registradas |
| `relations` | lista de relações | Relações declaradas pelo usuário |
| `evidence_refs` | lista de strings | Referências de evidência |

Cada `RepositoryRef` mantém nome, root, tipo, manifesto de projeto e nível de
evidência. O workspace não move, mescla ou reescreve `.git`.

## Fluxo

```text
apiforge workspace init --root <workspace>
apiforge workspace add <repository> --root <workspace>
apiforge workspace status --root <workspace>
```

Roots ausentes, relações não suportadas e sinais insuficientes continuam em
`unresolved`.
