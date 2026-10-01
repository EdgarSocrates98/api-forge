# GitHubPrReceipt/v1

`af-github-pr-receipt/1` is emitted only by the dedicated CI host script in
`scripts/github_pr_host.py`. It is not an API Forge core mutation contract.

The receipt records repository, base and head refs, the host operation
(`create_or_reuse` or `enable_auto_merge`), the GitHub read-back of the pull
request, observation time and whether the operation was a dry run. For
`enable_auto_merge`, `pull_request_before` and `pull_request_after` preserve
the read-back surrounding the mutation request. It states the limitation that
it proves the host request/read-back, not approval identity, eventual merge or
deployment safety.

The mutation boundary requires `APIFORGE_HOST_APPROVED=true`, a GitHub token
provided by the CI host and an idempotent lookup before creation. Agents,
skills and `src/apiforge` do not call this script. The optional auto-merge job
is enabled only by the repository variable `APIFORGE_AUTO_MERGE=true` and is
still subject to branch protection and GitHub's own approval rules.
