# Governança do GitHub no API Forge

[English](API_FORGE_GITHUB_GOVERNANCE.en.md) · [Uso da plataforma](API_FORGE_PLATFORM_USAGE.md)

O workflow de CI valida cada branch e abre PRs verdes, mas disciplina de
workflow não é enforcement. O GitHub garante merges pelo ruleset `protect` e
pelo `.github/CODEOWNERS`. O agente nunca altera o ruleset:
`scripts/github_ruleset_plan.py` só gera um plano que o dono revisa e aplica.
`scripts/github_pr_host.py` continua sendo a única fronteira de mutação no
GitHub.

## Estado atual (lido em 2026-09-28)

- `protect` está `active`, mas `conditions.ref_name.include` está vazio: ele
  **não se aplica a nenhuma branch**, então nenhuma regra vale hoje.
- `required_status_checks` não lista nenhum check.
- A regra `pull_request` exige revisão de code owner; o `.github/CODEOWNERS`
  agora existe, então essa regra passa a valer assim que o ruleset apontar
  para uma branch.
- Existem as regras `update`, `creation`, `required_signatures`,
  `required_linear_history`, `non_fast_forward` e `deletion`; não há bypass.

## Planejar e aplicar

```bash
gh api repos/EdgarSocrates98/api-forge/rulesets/23971496 > ruleset.json
python scripts/github_ruleset_plan.py --input ruleset.json --payload-out plan-payload.json
# revise "warnings" e plan-payload.json, então:
gh api -X PUT repos/EdgarSocrates98/api-forge/rulesets/23971496 --input plan-payload.json
```

O plano aponta para `~DEFAULT_BRANCH`, exige `Validate project` e
`Validate API/Git/CI replay control plane` em modo strict, mantém as outras
regras e imprime um `plan_sha256`. Entrada inválida é recusada com
`AF-GITHUB-RULESET-INVALID`.

## Decida antes de aplicar

| Situação | Opção | Efeito |
|---|---|---|
| Mantenedor único, quer auto-merge | `--bypass-owner` | Admins do repositório (role id 5) fazem bypass em modo `pull_request`: PR continua obrigatório, mas o admin pode mesclar sem cumprir as regras, **inclusive os checks obrigatórios** |
| Checks valendo para todos | `--drop-rule update` | Remove a restrição de update que bloquearia merges de PR; a revisão de code owner exige uma aprovação que você não pode dar no próprio PR |
| Existe segundo mantenedor | sem flags | Tudo vale; o outro mantenedor aprova as revisões de code owner |

`update` restringe qualquer atualização da branch alvo: mantida sem bypass,
bloqueia merges de PR. `required_signatures` recusa pushes locais sem
assinatura; commits de merge e squash feitos pelo GitHub são assinados.

Proteja o próprio `.github/CODEOWNERS` (ele está listado com dono) para que
responsabilidades não mudem sem revisão.
