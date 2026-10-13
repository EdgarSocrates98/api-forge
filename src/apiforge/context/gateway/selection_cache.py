"""L4 selection cache: the evidence selection is cached, the capsule envelope is not.

The capsule fingerprint embeds the case id, which changes with any analyzed
input, so caching whole capsules would either serve a stale fingerprint or
miss on every edit. The expensive part — graph impact, schema resolution,
model scan and handler slicing — is the ``Selection``; it is keyed by the
request and guarded by dependency probes (files, graph neighborhood and a
symbol scan of changed sources), so an unrelated edit keeps the hit and a
relevant one invalidates it.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import yaml

from apiforge.cache.store import CacheStore
from apiforge.context.gateway.canonical import dumps
from apiforge.context.gateway.levels import _TEST_FILE, Candidate, Selection
from apiforge.contracts.cache import CacheDecision, CacheDep
from apiforge.index.treehash import SOURCE_EXTS

SELECTION_VERSION = "selection/1"
LAYER = "capsule"
_TEST_NAME = _TEST_FILE


def selection_key(target: str, impact: str, contract: str, project: str) -> str:
    body = {
        "v": SELECTION_VERSION,
        "target": target,
        "impact": impact,
        "contract": contract,
        "project": project,
    }
    return hashlib.sha256(dumps(body)).hexdigest()


def serialize(selection: Selection) -> str:
    body = {
        "v": SELECTION_VERSION,
        "impact": dict(sorted(selection.impact.items())),
        "policies": list(selection.policies),
        "unresolved": list(selection.unresolved),
        "graph_ready": selection.graph_ready,
        "candidates": [
            {
                "content": c.content,
                "kind": c.kind,
                "label": c.label,
                "source": c.source,
                "provenance": c.provenance,
                "origin": c.origin,
                "span": list(c.span) if c.span else None,
                "parity": c.parity,
                "delta": {k: list(v) for k, v in sorted(c.delta.items())},
            }
            for c in selection.candidates
        ],
    }
    return dumps(body).decode("utf-8")


def restore(payload: str, fingerprint: dict[str, object]) -> Selection | None:
    try:
        body = json.loads(payload)
        if body.get("v") != SELECTION_VERSION:
            return None
        candidates = [
            Candidate(
                content=str(item["content"]),
                kind=item["kind"],
                label=str(item["label"]),
                source=str(item["source"]),
                provenance=str(item["provenance"]),
                origin=item["origin"],
                span=(int(item["span"][0]), int(item["span"][1])) if item.get("span") else None,
                parity=item.get("parity"),
                delta={k: tuple(v) for k, v in (item.get("delta") or {}).items()},
            )
            for item in body["candidates"]
        ]
    except (ValueError, KeyError, TypeError):
        return None
    return Selection(
        fingerprint=fingerprint,
        impact={str(k): int(v) for k, v in body["impact"].items()},
        candidates=candidates,
        policies=tuple(body["policies"]),
        unresolved=list(body["unresolved"]),
        graph_ready=bool(body.get("graph_ready")),
    )


def file_sha(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def span_sha(path: Path, span: tuple[int, int]) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    if span[1] > len(lines):
        return None
    text = chr(10).join(lines[span[0] - 1 : span[1]])
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def pointer_sha(
    path: Path, pointers: tuple[str, ...], cache: dict[Path, Any] | None = None
) -> str | None:
    if cache is not None and path in cache:
        document = cache[path]
    else:
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            return None
        if cache is not None:
            cache[path] = document
    values = [_resolve(document, pointer) for pointer in pointers]
    return hashlib.sha256(dumps(values)).hexdigest()


def dep_sha(root: Path, dep: CacheDep, documents: dict[Path, Any] | None = None) -> str | None:
    path = root / dep.path
    if dep.span is not None:
        return span_sha(path, dep.span)
    if dep.pointers:
        return pointer_sha(path, dep.pointers, documents)
    return file_sha(path)


def pointer(*parts: str) -> str:
    return "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in parts)


def _resolve(document: Any, text: str) -> Any:
    node = document
    for raw in text.split("/")[1:]:
        part = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, Mapping) and part in node:
            node = node[part]
        else:
            return None
    return json.loads(json.dumps(node, default=str))


def neighborhood(nodes: Iterable[Any], edges: Iterable[Any], wanted: Iterable[str]) -> str:
    """Hash of the dependency nodes' own hashes plus every edge touching them.

    ``described_by`` edges point at the contract node, whose id embeds the
    whole-contract hash; contract evidence is tracked by pointer deps instead.
    """
    ids = set(wanted)
    rows = sorted(f"node|{node.id}|{node.sha256}" for node in nodes if node.id in ids) + sorted(
        f"edge|{edge.from_id}|{edge.kind.value}|{edge.to_id}"
        for edge in edges
        if (edge.from_id in ids or edge.to_id in ids) and edge.kind.value != "described_by"
    )
    return hashlib.sha256(chr(10).join(rows).encode("utf-8")).hexdigest()


def manifest_text(root: Path, project: Path) -> str:
    rows = {path: sha for path, sha in _manifest(root, project).items()}
    return dumps(rows).decode("utf-8")


def _manifest(root: Path, project: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    if not project.is_dir():
        return rows
    for path in sorted(project.rglob("*")):
        if path.suffix not in SOURCE_EXTS or not path.is_file():
            continue
        if ".apiforge" in path.parts or "__pycache__" in path.parts:
            continue
        digest = file_sha(path)
        if digest is not None:
            rows[_rel(path, root)] = digest
    return rows


def dependencies(
    root: Path,
    selection: Selection,
    target_id: str,
    contract_rel: str,
    route_facts: Iterable[str],
) -> tuple[list[CacheDep], list[str], list[str]]:
    """(deps, nodes, symbols) the selection was derived from, as narrow as the evidence."""
    deps: dict[tuple[str, tuple[int, int] | None, tuple[str, ...]], CacheDep] = {}
    method, _, path = target_id.removeprefix("operation:").partition(" ")
    contract_pointers = {pointer("paths", path, method.lower())}
    for candidate in selection.candidates:
        prefix, _, name = candidate.label.partition(":")
        if candidate.kind == "schema" and name:
            contract_pointers.add(pointer("components", "schemas", name))
            continue
        if candidate.kind == "contract":
            continue
        source = candidate.source
        if not source or source.startswith(".apiforge/") or Path(source).is_absolute():
            continue
        if candidate.span is not None:
            dep = CacheDep(path=source, span=candidate.span)
        else:
            dep = CacheDep(path=source)
        deps[(dep.path, dep.span, dep.pointers)] = dep
    if contract_rel and not Path(contract_rel).is_absolute():
        dep = CacheDep(path=contract_rel, pointers=tuple(sorted(contract_pointers)))
        deps[(dep.path, None, dep.pointers)] = dep
    documents: dict[Path, Any] = {}
    recorded = [
        dep.model_copy(update={"sha256": dep_sha(root, dep, documents)}) for dep in deps.values()
    ]
    nodes = {target_id, *route_facts}
    located: dict[str, str] = {}
    schemas: set[str] = set()
    symbols: set[str] = set()
    for candidate in selection.candidates:
        prefix, _, name = candidate.label.partition(":")
        if candidate.provenance.startswith("graph-edge:backed_by:"):
            nodes.add(candidate.provenance.removeprefix("graph-edge:backed_by:"))
        if prefix == "schema" and name:
            schemas.add(name)
        elif prefix == "model" and name and candidate.span is not None:
            located[name] = f"{candidate.source}:{candidate.span[0]}-{candidate.span[1]}"
        elif prefix == "handler" and name:
            symbols.add(f"test:{name}")
    for name in schemas:
        symbols.add(f"model:{name}@{located[name]}" if name in located else f"model:{name}")
    return recorded, sorted(nodes), sorted(symbols)


_DEFINITION = r"\b(?:class|interface|record|enum|struct|type|data\s+class)\s+{name}\b"


def _definition_hit(path: str, body: str, symbol: str) -> str | None:
    """A (new) definition of a selected schema's model outside its recorded location."""
    name, _, where = symbol.removeprefix("model:").partition("@")
    recorded_path, _, span = where.partition(":")
    start, _, end = span.partition("-")
    for match in re.finditer(_DEFINITION.format(name=re.escape(name)), body):
        line = body.count(chr(10), 0, match.start()) + 1
        if where and path == recorded_path and int(start) <= line <= int(end):
            continue
        return f"changed source {path}:{line} defines {name}"
    return None


class RootProbe:
    """Current state of a root as seen by the freshness assessment."""

    def __init__(
        self,
        root: Path,
        project: Path,
        store: CacheStore,
        nodes: list[Any],
        edges: list[Any],
    ) -> None:
        self.root = root
        self.project = project
        self.store = store
        self.nodes = nodes
        self.edges = edges
        self._current: dict[str, str] | None = None
        self._documents: dict[Path, Any] = {}
        self._dep_paths: set[str] = set()

    def exclude(self, paths: Iterable[str]) -> None:
        """Files already guarded by their own dependency probes skip the symbol scan."""
        self._dep_paths = set(paths)

    def dep_sha(self, dep: CacheDep) -> str | None:
        return dep_sha(self.root, dep, self._documents)

    def neighborhood_sha(self, nodes: tuple[str, ...]) -> str | None:
        return neighborhood(self.nodes, self.edges, nodes)

    def symbol_changed(self, manifest_uri: str, symbols: tuple[str, ...]) -> str | None:
        text = self.store.read_object(manifest_uri)
        if text is None:
            return "source manifest unavailable"
        recorded: Mapping[str, str] = json.loads(text)
        if self._current is None:
            self._current = _manifest(self.root, self.project)
        changed = sorted(path for path, sha in self._current.items() if recorded.get(path) != sha)
        handlers = [s.removeprefix("test:") for s in symbols if s.startswith("test:")]
        mention = (
            re.compile("|".join(rf"(?<![\w]){re.escape(name)}(?![\w])" for name in handlers))
            if handlers
            else None
        )
        for path in changed:
            try:
                body = (self.root / path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for symbol in symbols:
                if symbol.startswith("model:"):
                    hit = _definition_hit(path, body, symbol)
                    if hit is not None:
                        return hit
            if (
                mention is not None
                and path not in self._dep_paths
                and _TEST_NAME.search(Path(path).name)
            ):
                match = mention.search(body)
                if match:
                    return f"changed test {path} mentions {match.group(0)}"
        return None


def lookup(store: CacheStore, key: str, probe: RootProbe) -> tuple[CacheDecision, str | None]:
    return store.lookup(LAYER, key, probe=probe)


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "LAYER",
    "SELECTION_VERSION",
    "RootProbe",
    "dep_sha",
    "dependencies",
    "file_sha",
    "lookup",
    "manifest_text",
    "neighborhood",
    "pointer",
    "restore",
    "selection_key",
    "serialize",
]
