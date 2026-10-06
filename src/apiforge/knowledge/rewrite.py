"""§39 query rewriting — only when deterministic retrieval failed AND the
declared budget and profile allow. The original and rewritten strings are
both recorded in the contract; a blocked gate never rewrites.
"""

from __future__ import annotations

from apiforge.contracts.model_routing import QueryRewrite

_PROFILES_ALLOWED = {"balanced", "deep"}


def rewrite_query(
    query: str,
    *,
    deterministic_hits: int,
    budget_remaining: dict[str, int | float | None] | None = None,
    profile: str = "balanced",
) -> QueryRewrite:
    """Gate first; only then produce the deterministic rewrite.

    The rewrite itself uses the declared expansion vocabulary (synonym groups
    from ``expand``): the rewritten query is the original plus the added
    expansion terms — deterministic, auditable, no model call.
    """
    if deterministic_hits > 0:
        return QueryRewrite(
            original=query,
            rewritten=None,
            gate="deterministic_succeeded",
            reason="deterministic retrieval succeeded; rewriting is forbidden",
        )
    budget = budget_remaining or {}
    rewrites = budget.get("rewrites")
    cost = budget.get("cost")
    if rewrites is not None and rewrites <= 0:
        return QueryRewrite(
            original=query,
            rewritten=None,
            gate="budget_blocked",
            reason="declared rewrite budget exhausted",
        )
    if cost is not None and cost <= 0:
        return QueryRewrite(
            original=query,
            rewritten=None,
            gate="budget_blocked",
            reason="declared cost budget exhausted",
        )
    if profile not in _PROFILES_ALLOWED:
        return QueryRewrite(
            original=query,
            rewritten=None,
            gate="profile_blocked",
            reason=f"profile '{profile}' does not allow query rewriting",
        )
    from apiforge.knowledge.retrieval import expand

    _, added = expand(query)
    rewritten = " ".join(dict.fromkeys((query, *added))) if added else query
    return QueryRewrite(
        original=query,
        rewritten=rewritten,
        gate="allowed",
        reason="deterministic retrieval failed; expansion terms appended",
    )


__all__ = ["rewrite_query"]
