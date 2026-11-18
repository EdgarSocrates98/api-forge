# Update e repair — api-forge

## Update

```bash
apiforge install update --to <versão ou tag pinada>
```

`latest` é recusado por contrato — sempre pin a versão. Sem checkout
registrado o update reporta BLOCKED honestamente.

## Repair

```bash
apiforge doctor   # mostra o drift
apiforge install repair   # reassegura regiões gerenciadas
```

Repair restaura arquivos gerenciados removidos e reassegura os blocos
`forge:api-forge`/`forge:ecosystem` dos consumer docs dentro de arquivos
seus — conteúdo fora do bloco nunca é tocado. `.mcp.json` é regravado com
o **mesmo argv** registrado no install (o `--surface` do
`--gateway-profile` persistido em `components.json`), nunca com um modo
diferente. Antes de sobrescrever, um snapshot vai para
`<state_dir>/backups/`.
