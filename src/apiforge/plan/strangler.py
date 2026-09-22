"""Strangler cut plan: baseline vs candidate `code.route` facts.

Route presence in the candidate proves the surface exists — it does not
prove behavioral parity. Every `migrated` entry names the evidence that
would close the cut: a contract diff and consumer confirmation. `missing`
routes are cut blockers; `stale` routes were unreachable in the baseline;
`added` routes are additive and carry no cut dependency.
"""

from __future__ import annotations

from collections.abc import Iterable

from apiforge.core.models import Fact

_CUT_EVIDENCE = (
    "diff contract baseline vs candidate for this operation",
    "consumer confirmation or contract test for this operation",
)


def strangler_plan(baseline: Iterable[Fact], candidate: Iterable[Fact]) -> dict[str, object]:
    """Compare route surfaces; emit a deterministic per-route cut plan."""
    base_routes = [f for f in baseline if f.kind == "code.route"]
    cand_routes = [f for f in candidate if f.kind == "code.route"]
    cand_keys = {
        (str(f.measures.get("method", "")).upper(), str(f.measures.get("path", "")))
        for f in cand_routes
        if f.attrs.get("reachable", True)
    }
    items: list[dict[str, object]] = []
    for fact in sorted(
        base_routes,
        key=lambda f: (str(f.measures.get("path")), str(f.measures.get("method"))),
    ):
        key = (
            str(fact.measures.get("method", "")).upper(),
            str(fact.measures.get("path", "")),
        )
        if not fact.attrs.get("reachable", True):
            status = "stale"
            evidence: tuple[str, ...] = ("confirm no live consumer before retiring",)
        elif key in cand_keys:
            status = "migrated"
            evidence = _CUT_EVIDENCE
        else:
            status = "missing"
            evidence = ("implement or retire this operation in the candidate",)
        items.append(
            {
                "method": key[0],
                "path": key[1],
                "status": status,
                "evidence_fact": fact.fact_id,
                "cut_requires": list(evidence),
            }
        )
    base_keys = {
        (str(f.measures.get("method", "")).upper(), str(f.measures.get("path", "")))
        for f in base_routes
    }
    for fact in sorted(
        cand_routes,
        key=lambda f: (str(f.measures.get("path")), str(f.measures.get("method"))),
    ):
        key = (
            str(fact.measures.get("method", "")).upper(),
            str(fact.measures.get("path", "")),
        )
        if key not in base_keys and fact.attrs.get("reachable", True):
            items.append(
                {
                    "method": key[0],
                    "path": key[1],
                    "status": "added",
                    "evidence_fact": fact.fact_id,
                    "cut_requires": [],
                }
            )
    counts = {
        s: sum(1 for i in items if i["status"] == s)
        for s in ("migrated", "missing", "stale", "added")
    }
    return {
        "baseline_routes": len(base_routes),
        "candidate_routes": len(cand_routes),
        "cut_ready": counts["missing"] == 0,
        "counts": counts,
        "items": items,
    }
