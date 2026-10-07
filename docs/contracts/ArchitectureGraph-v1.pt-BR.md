# ArchitectureGraph-v1 (PT-BR)

Projeção local e determinística sobre claims de workspace, repository, service,
contract, dependency e runtime.

[English](ArchitectureGraph-v1.md) · [ContextScope-v1](ContextScope-v1.pt-BR.md)

Cada relação contém `source`, `from_id`, `to_id`, `EvidenceRecord` e limitações.
Os níveis são distintos:

```text
observed · declared · inferred · heuristic · verified · unknown
```

O graph é limitado a repositórios declarados e sinais locais read-only. Um
repositório ausente, uma relação não suportada ou um input stale aparece em
`unresolved`. O graph não prova deploy, tráfego de runtime, dependência de
produção ou capability do host.

```text
apiforge workspace status --root <workspace>
apiforge context resolve --root <workspace> --scope workspace
```
