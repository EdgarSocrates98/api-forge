"""Build GraphAccessIR and DomainGraphSketch from ``data.graph.query`` facts.

The sketch only names labels and edges written in the code: a Cypher
pattern ``(a:A)-[:R]->(b:B)`` yields ``(A, R, B)``; a Gremlin traversal
yields ``(label?, edge, None)``. Nothing about the live graph is inferred.
"""

from __future__ import annotations

import re

from apiforge.adapters.graph_.extract import FACT_KIND
from apiforge.adapters.inventory import CodeInventory
from apiforge.contracts.graph_access import DomainGraphSketch, GraphAccessIR, GraphCallSite
from apiforge.core.ids import stable_id

_TRIPLE = re.compile(
    r"\(\s*\w*\s*:\s*`?(\w+)`?[^)]*\)\s*(<?)-\[\s*\w*\s*:\s*`?(\w+)`?[^\]]*\]-(>?)\s*"
    r"\(\s*\w*\s*:\s*`?(\w+)`?[^)]*\)"
)


def _strings(value: object) -> tuple[str, ...]:
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value)
    return ()


def _edges(
    language: str, text: str, labels: tuple[str, ...], edge_labels: tuple[str, ...]
) -> set[tuple[str | None, str, str | None]]:
    found: set[tuple[str | None, str, str | None]] = set()
    if language == "opencypher":
        for left, back, rel, _fwd, right in _TRIPLE.findall(text):
            found.add((right, rel, left) if back else (left, rel, right))
        return found
    if language == "gremlin":
        source = labels[0] if len(labels) == 1 else None
        found.update((source, edge, None) for edge in edge_labels)
    return found


def build_graph_access_ir(inventory: CodeInventory) -> GraphAccessIR:
    """Aggregate graph call sites; dynamic or unparsed sites stay unresolved."""
    sites: list[GraphCallSite] = []
    vertex_labels: set[str] = set()
    edge_labels: set[str] = set()
    edges: set[tuple[str | None, str, str | None]] = set()
    evidence: set[str] = set()
    vendors: set[str] = set()
    for fact in inventory.facts:
        if fact.kind != FACT_KIND:
            continue
        m = fact.measures
        labels = _strings(m.get("labels_used"))
        edge_names = _strings(m.get("edge_labels_used"))
        language = str(m["language"])
        text = m.get("query_text")
        sites.append(
            GraphCallSite(
                fact_id=fact.fact_id,
                vendor=m["vendor"],  # type: ignore[arg-type]
                language=language,  # type: ignore[arg-type]
                operation=str(m["operation"]),
                path=fact.source.path,
                line=fact.source.line or 0,
                sha256=fact.source.sha256,
                query_text=str(text) if text is not None else None,
                query_dynamic=bool(m.get("query_dynamic")),
                bounded=bool(m.get("bounded")),
                mutation=bool(m.get("mutation")),
                labels_used=labels,
                edge_labels_used=edge_names,
                shape_risks=_strings(m.get("shape_risks")),  # type: ignore[arg-type]
            )
        )
        vendors.add(str(m["vendor"]))
        vertex_labels.update(labels)
        edge_labels.update(edge_names)
        if labels or edge_names:
            evidence.add(f"{fact.source.path}:{fact.source.line}")
        edges |= _edges(language, str(text or ""), labels, edge_names)
    sketch = DomainGraphSketch(
        vertex_labels=tuple(sorted(vertex_labels)),
        edge_labels=tuple(sorted(edge_labels)),
        edges=tuple(sorted(edges, key=lambda e: (e[1], e[0] or "", e[2] or ""))),
        evidence=tuple(sorted(evidence)),
    )
    return GraphAccessIR(
        id=stable_id("graphaccess", {"root": inventory.root}),
        root=inventory.root,
        vendors=tuple(sorted(vendors)),  # type: ignore[arg-type]
        call_sites=tuple(sorted(sites, key=lambda s: (s.path, s.line, s.fact_id))),
        sketch=sketch,
        unresolved=tuple(sorted({d.code for d in inventory.diagnostics})),
    )
