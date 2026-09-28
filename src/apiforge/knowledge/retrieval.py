"""Deterministic retrieval (§56–58): expand, rank with explicit signals, return progressively.

Passages are the ``##`` sections of the local knowledge packs. A query is
expanded with the declared synonym groups (never by a model), passages are
scored by heading and body hits plus a bonus when the pack is the one the
expertise selector would load, and results come in tiers: top 3, then top 5,
then up to 20. Each passage is stored in the ctx CAS so it can be expanded or
cited by reference.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_extras import Passage, RetrievalResult

EXPANSION_FILE = Path(__file__).resolve().parents[1] / "rules" / "query_expansion.yaml"
TIER_SIZES = {1: 3, 2: 5, 3: 20}
_WORD = re.compile(r"[a-z0-9][a-z0-9-]*")


@lru_cache(maxsize=2)
def load_expansion(path: Path = EXPANSION_FILE) -> tuple[dict[str, Any], ...]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ContractError("AF-RETRIEVAL-EXPANSION-INVALID", f"{path}: {exc}") from exc
    if raw.get("schema") != "apiforge/query-expansion/v1":
        raise ContractError("AF-RETRIEVAL-EXPANSION-INVALID", f"{path}: unexpected schema")
    return tuple(
        {
            "id": str(row["id"]),
            "cues": tuple(str(item).lower() for item in row.get("cues") or ()),
            "terms": tuple(str(item).lower() for item in row.get("terms") or ()),
        }
        for row in raw.get("groups") or ()
    )


def expand(query: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(all terms, terms added by expansion)."""
    text = " ".join(query.lower().split())
    base = [word for word in _WORD.findall(text) if len(word) > 2]
    added: list[str] = []
    for group in load_expansion():
        if any(re.search(r"(?<![\w])" + re.escape(cue), text) for cue in group["cues"]):
            added.extend(term for term in group["terms"] if term not in base and term not in added)
    return tuple(dict.fromkeys([*base, *added])), tuple(added)


@lru_cache(maxsize=4)
def _passages(root: str) -> tuple[tuple[str, str, str, str], ...]:
    rows: list[tuple[str, str, str, str]] = []
    for pack in sorted(Path(root).iterdir()):
        if not pack.is_dir() or pack.name.startswith(("_", ".")):
            continue
        for doc in sorted(pack.glob("*.md")):
            text = doc.read_text(encoding="utf-8", errors="replace")
            sections = re.split(r"(?m)^## ", text)
            title = (
                sections[0].strip().splitlines()[0].lstrip("# ").strip()
                if sections[0].strip()
                else doc.stem
            )
            if len(sections) == 1:
                rows.append((pack.name, doc.name, title, text))
                continue
            for section in sections[1:]:
                heading, _, body = section.partition("\n")
                rows.append((pack.name, doc.name, heading.strip(), body))
    return tuple(rows)


def _hits(text: str, terms: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(1 for term in terms if re.search(r"(?<![\w])" + re.escape(term), lowered))


def search(
    query: str,
    *,
    tier: int = 1,
    root: Path | None = None,
    store_root: Path | None = None,
) -> RetrievalResult:
    from apiforge.context.gateway.refs import CtxStore
    from apiforge.knowledge.selector import default_root, select_expertise

    if tier not in TIER_SIZES:
        error = ContractError("AF-RETRIEVAL-TIER-INVALID", f"tier {tier} is not 1|2|3")
        error.field = "tier"  # type: ignore[attr-defined]
        error.unlock = "pass --tier 1, 2 or 3"  # type: ignore[attr-defined]
        raise error
    terms, added = expand(query)
    packs_root = default_root(root)
    selected = {item.pack_id for item in select_expertise(query, root=packs_root).selected}
    scored: list[tuple[float, str, str, str, str, dict[str, float]]] = []
    for pack, doc, heading, body in _passages(str(packs_root.resolve())):
        heading_hits = _hits(heading, terms)
        body_hits = _hits(body, terms)
        if not heading_hits and not body_hits:
            continue
        signals = {
            "heading_hits": float(heading_hits),
            "body_hits": float(body_hits),
            "selected_pack": 1.0 if pack in selected else 0.0,
        }
        score = 3 * heading_hits + body_hits + 2 * signals["selected_pack"]
        scored.append((-score, pack, doc, heading, body, signals))
    scored.sort(key=lambda row: (row[0], row[1], row[2], row[3]))
    size = TIER_SIZES[tier]
    store = CtxStore(Path(store_root or Path.cwd()))
    passages = tuple(
        Passage(
            pack_id=pack,
            file=doc,
            heading=heading,
            score=-score,
            signals=signals,
            ref=store.put(f"## {heading}\n{body}"),
            bytes=len(body.encode("utf-8")),
        )
        for score, pack, doc, heading, body, signals in scored[:size]
    )
    more = len(scored) > size and tier < 3
    return RetrievalResult(
        query=query,
        expanded_terms=terms,
        added_terms=added,
        tier=tier,
        passages=passages,
        candidates=len(scored),
        next_tier=tier + 1 if more else None,
        unresolved=() if passages else ("no-passage-matched",),
    )


__all__ = ["expand", "load_expansion", "search"]
