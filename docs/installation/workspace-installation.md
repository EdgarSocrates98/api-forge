# Instalação em workspace — api-forge

Monorepo/pasta com vários projetos:

```bash
cd ~/minha-workspace
theforge install auto --scope workspace
# ou membro explícito (repetível):
theforge install auto --scope workspace --member sub/repo

# ou este forge direto, num root autoritativo:
apiforge install --scope workspace --root ~/minha-workspace --yes
```

Resolução do alvo (`installkit 1.0.6`): `--root` sempre vence — inclusive
quando um `forge.workspace.yaml`/`.forge-workspace`/`pyproject.toml` de
workspace ou um `.git` existe num ancestral. Sem `--root`, o installkit
procura marcador de workspace subindo do cwd, depois `.git`, e por fim o
cwd.

Membros: a descoberta (`discover_projects`) conta diretório como projeto
quando ele carrega **qualquer** marcador — `.git`, `forge.json`,
`forge.agentic.json`, `pyproject.toml` ou `package.json` — então membro
**gitless é first-class**: `.git` não é requisito. A varredura cobre até
2 níveis, não segue symlink/junction, pula diretórios ocultos e
`IGNORED_DIRS`, e nunca desce dentro de um membro já descoberto (os
módulos internos ficam isolados).

Precedência: `project > workspace > user` — um membro que já tem
instalação `project` deste forge (estado `.apiforge/install/` ou chave
MCP própria em `.mcp.json`) nunca é silenciosamente ampliado pelo install
de workspace; conflitos são reportados, nunca sobrescritos.

Cada install `workspace` grava `forge/WorkspaceInstall/v1` em
`.apiforge/install/workspace-install.json` — root servido + `receipt_id`
— o documento que o plano consolidado lê. Estado e ledger ficam isolados
por root — nenhum runtime duplicado.
