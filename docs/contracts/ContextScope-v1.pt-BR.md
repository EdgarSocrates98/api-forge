# ContextScope-v1 (PT-BR)

O contexto é resolvido internamente pelo API Forge; `apiforge here` foi
adiado. Os escopos fechados são:

[English](ContextScope-v1.md) · [Guia portátil](../guides/API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md)

- `repo`: contexto do repositório/projeto atual;
- `workspace`: contexto do workspace virtual declarado;
- `target`: um alvo observado, selecionado por ID estável, label ou root.

`impact` é opcional e aceita `direct`, `transitive` ou `all`.

O resultado contém targets selecionados, repositórios incluídos, graph, funnel
medido, evidências, gaps e diagnósticos `unresolved`. CLI, MCP, JSON, TUI e
adapters de host devem projetar esse payload sem alterar status ou evidência.

```text
apiforge context resolve --scope repo
apiforge context resolve --scope workspace --impact direct
apiforge context resolve --scope target --target repository:<id>
```
