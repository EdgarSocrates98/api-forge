# Update e repair — api-forge

## Update

```bash
apiforge install update --to <versão ou tag pinada>
```

`latest` é recusado por contrato — sempre pin a versão. Sem checkout
registrado o update reporta BLOCKED honestamente.

## Repair

```bash
apiforge install doctor   # mostra o drift (ledger + .mcp.json + handshake)
apiforge install repair   # reassegura regiões gerenciadas
```

Repair restaura arquivos gerenciados removidos e reassegura os blocos
`forge:api-forge`/`forge:ecosystem` dos consumer docs dentro de arquivos
seus — conteúdo fora do bloco nunca é tocado. `.mcp.json` é regravado com
o **mesmo argv** registrado no install (o `--surface` do
`--gateway-profile` persistido em `components.json`, resolvido para o
mesmo caminho absoluto), nunca com um modo diferente. Antes de
sobrescrever, um snapshot vai para `<state_dir>/backups/`.

Todo recibo (`install`, `repair`, `uninstall`, `update`) e todo documento
de saúde (`status`, `doctor`) carrega o bloco `lifecycle`
(`forge/InstallLifecycle/v1`): `planned`/`blocked`/`failed`/`applied`/
`partially_applied`/`verified`/`unverified`/`ready`/`certified` — derivado
do recibo, nunca declarado pelo escritor. `status: completed` sozinho
deriva `verified`; `ready` exige saúde verde no `status`/`doctor`.
