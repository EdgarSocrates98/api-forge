"""Local indexes derived from extractor output — files, symbols, routes, facts.

All four index files are canonical JSONL under `<root>/.apiforge/index/`.
The index covers what the extractor sees: route handlers and the facts they
produced. Files without routes are named in `unresolved` rather than
silently absent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.contracts.base import ContractError
from apiforge.index.treehash import source_digest

INDEX_DIR = "index"
INDEX_VERSION = "index/1"

_FRAMEWORK_EXTRACTORS: dict[str, Any] = {}


def _extractors() -> dict[str, Any]:
    if not _FRAMEWORK_EXTRACTORS:
        from apiforge.adapters.fastapi.extractor import extract_fastapi
        from apiforge.adapters.go.extractor import extract_go
        from apiforge.adapters.spring.extractor import extract_spring

        _FRAMEWORK_EXTRACTORS.update(
            {"fastapi": extract_fastapi, "go": extract_go, "spring": extract_spring}
        )
    return _FRAMEWORK_EXTRACTORS


def _detect(project: Path) -> str:
    from apiforge.application.analyze import _detect_framework

    return _detect_framework(project)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "".join(
        json.dumps(r, sort_keys=True, separators=(",", ":"), default=str) + "\n"
        for r in rows
    )
    path.write_text(text, encoding="utf-8", newline="")


def build_index(
    project: Path,
    root: Path,
    framework: str = "auto",
    inventory: CodeInventory | None = None,
) -> dict[str, Any]:
    """Write the four index files plus `index.json` manifest."""
    project = Path(project)
    if not project.is_dir():
        raise ContractError("AF-INDEX-NOT-FOUND", str(project))
    if framework == "auto":
        framework = _detect(project)
    extractor = _extractors().get(framework)
    if extractor is None:
        raise ContractError(
            "AF-INDEX-FRAMEWORK", f"no extractor for framework {framework!r}"
        )
    if inventory is None:
        inventory = extractor(project)

    digest, files = source_digest(project)
    routes: list[dict[str, Any]] = []
    symbols: list[dict[str, Any]] = []
    facts: list[dict[str, Any]] = []
    routed_files: set[str] = set()
    for fact in inventory.facts:
        facts.append(
            {
                "fact_id": fact.fact_id,
                "kind": fact.kind,
                "line": fact.source.line,
                "path": fact.source.path,
            }
        )
        if fact.kind == "code.route":
            measures = dict(fact.measures)
            routes.append(
                {
                    "fact_id": fact.fact_id,
                    "function": fact.attrs.get("function"),
                    "line": fact.source.line,
                    "method": measures.get("method"),
                    "path": measures.get("path"),
                    "source": fact.source.path,
                }
            )
            routed_files.add(str(fact.source.path))
            if fact.attrs.get("function"):
                symbols.append(
                    {
                        "kind": "handler",
                        "line": fact.source.line,
                        "name": fact.attrs.get("function"),
                        "path": fact.source.path,
                    }
                )
    routes.sort(key=lambda r: (str(r["method"]), str(r["path"]), str(r["source"])))
    symbols.sort(key=lambda s: (str(s["path"]), s["line"] or 0, str(s["name"])))
    facts.sort(key=lambda f: str(f["fact_id"]))
    unrouted = sorted(
        f["path"] for f in files if f["path"] not in routed_files
    )

    out = Path(root) / ".apiforge" / INDEX_DIR
    out.mkdir(parents=True, exist_ok=True)
    _write_jsonl(out / "files.jsonl", files)
    _write_jsonl(out / "symbols.jsonl", symbols)
    _write_jsonl(out / "routes.jsonl", routes)
    _write_jsonl(out / "facts.jsonl", facts)
    manifest = {
        "index_version": INDEX_VERSION,
        "framework": framework,
        "source_digest": digest,
        "counts": {
            "files": len(files),
            "symbols": len(symbols),
            "routes": len(routes),
            "facts": len(facts),
        },
        "unresolved": {
            "files_without_routes": unrouted,
            "note": "index covers extractor-visible symbols only",
        },
    }
    (out / "index.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def index_status(project: Path, root: Path) -> dict[str, Any]:
    """Compare the live tree against files.jsonl — name added/changed/removed."""
    out = Path(root) / ".apiforge" / INDEX_DIR
    manifest_path = out / "index.json"
    files_path = out / "files.jsonl"
    if not manifest_path.is_file() or not files_path.is_file():
        raise ContractError(
            "AF-INDEX-NOT-BUILT", f"no index under {out} — run `index build`"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    old = {
        r["path"]: r
        for r in (
            json.loads(line)
            for line in files_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    digest, rows = source_digest(Path(project))
    new = {r["path"]: r for r in rows}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(
        p for p in set(new) & set(old) if new[p]["sha256"] != old[p]["sha256"]
    )
    return {
        "index_version": manifest.get("index_version"),
        "source_digest": digest,
        "indexed_digest": manifest.get("source_digest"),
        "stale": digest != manifest.get("source_digest"),
        "added": added,
        "removed": removed,
        "changed": changed,
        "counts": manifest.get("counts", {}),
    }
