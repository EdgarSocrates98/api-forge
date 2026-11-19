# Troubleshooting — API Forge (EN)

| Symptom | Action |
|---|---|
| `command not found: apiforge` | run `./setup.sh` again; open a **new** terminal (launcher lands on PATH) |
| `FORGE-INSTALL-LOCKED` | another install is running or was interrupted; the lock expires and is recovered automatically — retry |
| `FORGE-INSTALL-PLAN-NOT-APPROVED` | mutations require `--yes` after reviewing `--dry-run` |
| `FORGE-INSTALL-NOT-A-REPO` | project scope needs a `.git` root or `--root` |
| `FORGE-INSTALL-DRIFT-UNREPAIRABLE` | managed content diverged beyond repair — `uninstall` + reinstall restores the managed surface |
| MCP `FAIL` + `stderr_tail` | missing dependency (e.g. the `mcp` extra) — install it and re-run `apiforge install verify` |
| `install status`/`doctor` exit ≠ 0 | the exit code follows `lifecycle.state`: `verified`/`ready`/`certified`/`planned`/`unverified`/`applied` → 0; `failed`/`blocked`/`partially_applied` → 1 — scripts can gate on it |
| stale/partial install | `uninstall` removes only ledger-owned files; `status`/`doctor` show the truth (`lifecycle.state`) |

Português: [troubleshooting.md](troubleshooting.md).
