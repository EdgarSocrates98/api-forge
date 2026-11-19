# Troubleshooting — api-forge

| Sintoma | Ação |
|---|---|
| `command not found: apiforge` | rode `./setup.sh` de novo; abra terminal novo (launcher no PATH) |
| `FORGE-INSTALL-LOCKED` | outra instalação em curso; se foi interrompida, o lock expira/recupera sozinho |
| `FORGE-INSTALL-PLAN-NOT-APPROVED` | mutações exigem `--yes` (após o `--dry-run`) |
| `FORGE-INSTALL-NOT-A-REPO` | escopo project precisa de `.git` ou `--root` |
| doctor FAIL em mcp-handshake | `apiforge install verify` mostra stderr_tail — geralmente dependência ausente (extra `mcp`) |
| arquivo seu sumiu? | não deveria — instalação nunca sobrescreve conteúdo do usuário; backups em `<state_dir>/backups/` |
| drift detectado (`status`/`doctor` `degraded`, lifecycle `partially_applied`) | `apiforge install repair` restaura regiões gerenciadas mantendo o resto |
| `install status`/`doctor` exit ≠ 0 | o exit code segue `lifecycle.state`: `verified`/`ready`/`certified`/`planned`/`unverified`/`applied` → 0; `failed`/`blocked`/`partially_applied` → 1 — scripts podem gatear nele |
