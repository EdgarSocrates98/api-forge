# apiforge/discovery.py
"""Offline retrieval for the install-2.0 §6.2/§6.4 discovery ops (lf-0037).

Every function returns a JSON-safe dict; the Typer commands in ``cli.py``
only adapt argv. Nothing here invents content — rules come from
``rules.catalog.load_catalog``, knowledge docs from
``knowledge.selector.default_root`` (repo checkout or packaged
``apiforge/_data/knowledge``), skills/agents from ``install.render`` —
the same resolution the installer uses. Absence degrades to an explicit
``None``/empty state, never to fabricated content.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge import __version__, discovery_ops

INDEX_FIELDS = ("rule_id", "area", "title", "severity", "runtime_scope")
DEFAULT_LIMIT = 50
MAX_LIMIT = 200
_SNIPPET_MAX = 3
_SNIPPET_WIDTH = 160


def _clamp_limit(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_LIMIT
    return max(1, min(int(limit), MAX_LIMIT))


def _cursor_offset(cursor: str | None) -> int:
    if cursor in (None, ""):
        return 0
    try:
        offset = int(str(cursor), 10)
    except ValueError:
        from apiforge.application.analyze import AnalysisError

        raise AnalysisError(
            "AF-CURSOR-INVALID", f"cursor must be a non-negative integer, got {cursor!r}"
        ) from None
    if offset < 0:
        from apiforge.application.analyze import AnalysisError

        raise AnalysisError(
            "AF-CURSOR-INVALID", f"cursor must be a non-negative integer, got {cursor!r}"
        )
    return offset


def _paginate(items: list[Any], limit: int | None, cursor: str | None) -> dict[str, Any]:
    offset = _cursor_offset(cursor)
    lim = _clamp_limit(limit)
    page = items[offset : offset + lim]
    nxt = offset + lim if offset + lim < len(items) else None
    return {
        "items": page,
        "total": len(items),
        "limit": lim,
        "offset": offset,
        "next_cursor": str(nxt) if nxt is not None else None,
    }


def _sha256_of(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _rules() -> list[Any]:
    from apiforge.rules.catalog import load_catalog

    return [meta for _rid, meta in sorted(load_catalog().items())]


def _rule_index(meta: Any) -> dict[str, Any]:
    return {
        "id": meta.rule_id,
        "area": meta.area,
        "title": meta.title,
        "severity": meta.severity.value,
        "runtime_scope": meta.runtime_scope,
    }


def rules_search(
    *,
    query: str | None = None,
    area: str | None = None,
    severity: str | None = None,
    limit: int | None = None,
    cursor: str | None = None,
    index: bool = False,
) -> dict[str, Any]:
    """§6.2 rules.search — case-insensitive keyword over
    id/title/area/rationale plus area/severity filters, offset-paginated."""
    metas = _rules()
    if area:
        a = area.upper()
        metas = [m for m in metas if a in m.area.upper()]
    if severity:
        sev = severity.lower()
        metas = [m for m in metas if m.severity.value == sev]
    if query:
        q = query.lower()
        metas = [
            m
            for m in metas
            if q
            in " ".join([m.rule_id, m.title or "", m.area or "", m.rationale or ""]).lower()
        ]
    items = [
        _rule_index(m) if index else (m.model_dump(mode="json") | {"id": m.rule_id})
        for m in metas
    ]
    page = _paginate(items, limit, cursor)
    return {
        "status": "ok",
        "forge": "apiforge",
        "filters_applied": {
            k: v
            for k, v in {"query": query, "area": area, "severity": severity}.items()
            if v is not None
        },
        "rules": page["items"],
        "total": page["total"],
        "limit": page["limit"],
        "next_cursor": page["next_cursor"],
    }


def _knowledge_root() -> Path:
    from apiforge.knowledge.selector import default_root

    return default_root(None)


def _knowledge_origin(root: Path) -> str:
    if (root.parent / "pyproject.toml").is_file():
        return "checkout"
    return "package" if "_data" in root.parts or "site-packages" in str(root) else "env"


def _knowledge_docs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def _doc_meta(root: Path, path: Path, *, term: str | None = None) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix()
    meta: dict[str, Any] = {
        "ref": rel,
        "pack": rel.split("/", 1)[0] if "/" in rel else None,
        "sha256": _sha256_of(path),
        "bytes": path.stat().st_size,
    }
    if term is None:
        return meta
    text = path.read_text(encoding="utf-8", errors="replace")
    needle = term.lower()
    hits = [
        (n, line.strip())
        for n, line in enumerate(text.splitlines(), 1)
        if needle in line.lower()
    ]
    meta["matched_lines"] = len(hits)
    meta["name_hit"] = needle in rel.lower()
    meta["snippets"] = [
        {"line": n, "text": s[:_SNIPPET_WIDTH]} for n, s in hits[:_SNIPPET_MAX]
    ]
    meta["snippets_truncated"] = len(hits) > _SNIPPET_MAX
    return meta


def knowledge_search(
    term: str,
    *,
    domain: str | None = None,
    limit: int | None = None,
    cursor: str | None = None,
) -> dict[str, Any]:
    """§6.2 knowledge.search — one hit per document with sha256 + provenance."""
    root = _knowledge_root()
    needle = term.lower()
    matched: list[Path] = []
    for path in _knowledge_docs(root):
        rel = path.relative_to(root).as_posix()
        if domain and not any(
            rel.split("/", 1)[0].startswith(p)
            for p in discovery_ops.domain_prefixes(domain)
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if needle in rel.lower() or needle in text.lower():
            matched.append(path)
    offset = _cursor_offset(cursor)
    lim = _clamp_limit(limit)
    window = matched[offset : offset + lim]
    nxt = offset + lim if offset + lim < len(matched) else None
    return {
        "status": "ok",
        "knowledge_root": str(root),
        "knowledge_origin": _knowledge_origin(root),
        "term": term,
        "domain": domain,
        "domain_prefixes": list(discovery_ops.domain_prefixes(domain)) if domain else None,
        "documents_total": len(matched),
        "documents": [_doc_meta(root, p, term=term) for p in window],
        "limit": lim,
        "next_cursor": str(nxt) if nxt is not None else None,
    }


def knowledge_get(file: str) -> dict[str, Any]:
    """§6.2 knowledge.get — resolved path + sha256 + provenance.

    ``file`` is a corpus-relative ref like ``rest-design/patterns.md``;
    traversal outside the knowledge root is refused with AF-PATH-OUTSIDE-ROOT.
    """
    from apiforge.application.analyze import AnalysisError

    root = _knowledge_root().resolve()
    target = (root / file).resolve()
    if not str(target).startswith(str(root) + "/") or target == root:
        raise AnalysisError("AF-PATH-OUTSIDE-ROOT", f"path escapes knowledge root: {file!r}")
    if not target.is_file():
        from apiforge.knowledge.loader import KnowledgeError

        raise KnowledgeError(
            "AF-KNOW-DOMAIN", f"{file!r} not present in knowledge root {root}"
        )
    return {
        "status": "ok",
        "knowledge_root": str(root),
        "knowledge_origin": _knowledge_origin(root),
        "document": {
            "ref": target.relative_to(root).as_posix(),
            "path": str(target),
            "sha256": _sha256_of(target),
            "bytes": target.stat().st_size,
        },
    }


def capabilities() -> dict[str, Any]:
    """§6.2 capabilities.list + protocol.describe in one document."""
    from apiforge.install import render

    rules = _rules()
    skills: list[str] = []
    agents: list[str] = []
    dirs = render.content_dirs()
    if dirs is not None:
        agents_src, skills_src = dirs
        if skills_src.is_dir():
            skills = sorted(d.name for d in skills_src.iterdir() if d.is_dir())
        if agents_src.is_dir():
            agents = sorted(p.stem for p in agents_src.glob("*.md"))
    root = _knowledge_root()
    docs = _knowledge_docs(root)
    packs = sorted({p.relative_to(root).parts[0] for p in docs}) if docs else []
    evals_root = None
    from apiforge.distribution.assets import package_root

    for cand in (package_root() / "_data" / "evals", root.parent / "evals"):
        if cand.is_dir():
            evals_root = cand
            break
    eval_suites = (
        sorted(d.name for d in evals_root.iterdir() if d.is_dir())
        if evals_root is not None
        else []
    )
    return {
        "status": "ok",
        "forge": "apiforge",
        "version": __version__,
        "cli": discovery_ops.CLI,
        "offline": True,
        "rules": {
            "count": len(rules),
            "areas": sorted({m.area for m in rules}),
            "severities": ["info", "low", "medium", "high", "critical"],
            "index_fields": list(INDEX_FIELDS),
        },
        "knowledge": {
            "root": str(root),
            "origin": _knowledge_origin(root),
            "documents": len(docs),
            "packs": packs,
        },
        "skills": {"count": len(skills), "ids": skills},
        "agents": {"count": len(agents), "ids": agents},
        "eval_suites": eval_suites,
        "domains": list(discovery_ops.DOMAINS),
        "protocols": list(discovery_ops.PROTOCOLS),
        "interfaces": {"mcp": discovery_ops.MCP_INTERFACE},
        "operations": discovery_ops.ops_expanded(),
    }


def context_pack(
    domain: str | None = None,
    *,
    rules_limit: int | None = None,
    knowledge_limit: int | None = None,
    as_of: str | None = None,
) -> dict[str, Any]:
    """§6.2 context.build — deterministic bounded pack: rule index entries +
    knowledge doc metadata (no content dump) + protocols + pack hash."""
    prefixes = discovery_ops.domain_prefixes(domain) if domain else None
    metas = _rules()
    if prefixes:
        metas = [
            m
            for m in metas
            if any(
                p in m.area.lower() or p in m.rule_id.lower() for p in prefixes
            )
        ]
    rlim = _clamp_limit(rules_limit)
    root = _knowledge_root()
    docs = _knowledge_docs(root)
    if prefixes:
        docs = [
            p
            for p in docs
            if any(p.relative_to(root).parts[0].startswith(px) for px in prefixes)
        ]
    klim = _clamp_limit(knowledge_limit)
    pack: dict[str, Any] = {
        "schema": "forge/context-pack/v1",
        "forge": "apiforge",
        "version": __version__,
        "domain": domain,
        "domain_prefixes": list(prefixes) if prefixes else None,
        "rules": [_rule_index(m) for m in metas[:rlim]],
        "rules_total": len(metas),
        "rules_truncated": len(metas) > rlim,
        "knowledge": {
            "root": str(root),
            "origin": _knowledge_origin(root),
            "documents": [_doc_meta(root, p) for p in docs[:klim]],
            "documents_total": len(docs),
            "truncated": len(docs) > klim,
        },
        "protocols": list(discovery_ops.PROTOCOLS),
        "operations": discovery_ops.ops(),
        "offline": True,
    }
    if as_of:
        pack["as_of"] = as_of
    pack["pack_sha256"] = hashlib.sha256(
        json.dumps(pack, sort_keys=True, ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    return pack
