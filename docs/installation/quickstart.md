# Quickstart — api-forge

Três comandos:

```bash
git clone <api-forge repo>
cd api-forge
./install.sh      # Windows: .\install.ps1 — account runtime + editable CLI
```

Depois, dentro de qualquer projeto:

```bash
cd ~/meu-projeto
apiforge install
```

Pronto. Abra seu AI host (Devin, Claude, Codex ou Copilot) — as skills do
api-forge já estão instaladas.

Em diretório vazio, `apiforge install` oculta `Current repository` e oferece
`Entire workspace`; escolha essa opção para manter instalação gerenciada no
diretório atual sem precisar inicializar Git.

## Verificar

```bash
apiforge status
apiforge doctor
```

Detalhes: [account-installation.md](account-installation.md). Problemas? → [troubleshooting.md](troubleshooting.md)
