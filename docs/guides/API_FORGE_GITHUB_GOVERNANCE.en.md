# API Forge GitHub Governance

[Português](API_FORGE_GITHUB_GOVERNANCE.md) · [Platform usage](API_FORGE_PLATFORM_USAGE.en.md)

The CI workflow validates every branch and opens green PRs, but workflow
discipline alone is not enforcement. GitHub enforces merges through the
`protect` ruleset and `.github/CODEOWNERS`. The agent never changes the
ruleset: `scripts/github_ruleset_plan.py` only produces a plan that the owner
reviews and applies. `scripts/github_pr_host.py` remains the only GitHub
mutation boundary of the project.

## Current state (read 2026-09-28)

- `protect` is `active` but `conditions.ref_name.include` is empty: it targets
  **no branch**, so none of its rules apply today.
- `required_status_checks` lists no check.
- The `pull_request` rule requires code-owner review; `.github/CODEOWNERS`
  now exists, so that rule becomes effective as soon as the ruleset targets a
  branch.
- Rules `update`, `creation`, `required_signatures`,
  `required_linear_history`, `non_fast_forward` and `deletion` are present;
  there are no bypass actors.

## Plan and apply

```bash
gh api repos/EdgarSocrates98/api-forge/rulesets/23971496 > ruleset.json
python scripts/github_ruleset_plan.py --input ruleset.json --payload-out plan-payload.json  # paths relative to the working directory
# review "warnings" and plan-payload.json, then:
gh api -X PUT repos/EdgarSocrates98/api-forge/rulesets/23971496 --input plan-payload.json
```

The plan targets `~DEFAULT_BRANCH`, requires `Validate project` and
`Validate API/Git/CI replay control plane` with the strict policy, keeps the
other rules and prints a `plan_sha256`. Malformed input is refused with
`AF-GITHUB-RULESET-INVALID`.

## Decide before applying

| Situation | Option | Effect |
|---|---|---|
| Single maintainer, auto-merge wanted | `--bypass-owner` | Repository admins (role id 5) bypass in `pull_request` mode: PRs are still required, but an admin can merge without meeting the rules, **including the required checks** |
| Keep checks binding for everyone | `--drop-rule update` | Removes the update restriction that would block PR merges; code-owner review then needs an approval you cannot give to your own PRs |
| Second maintainer available | no flags | Everything binds; the other maintainer approves code-owner reviews |

`update` restricts all updates of the targeted branch: kept without a bypass,
it blocks PR merges. `required_signatures` rejects unsigned local pushes;
merge and squash commits made by GitHub are signed.

Protect `.github/CODEOWNERS` itself (it is listed as owned by the owner) so
responsibilities cannot be changed without review.
