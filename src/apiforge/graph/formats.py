"""System-graph projections for graph databases — Neptune Gremlin CSV and RDF N-Triples.

Both writers are byte-deterministic: columns, rows and triples are
sorted, every property is written as ``:String`` (types are never guessed)
and nested values are canonical JSON. The validators re-read the files
offline against the loader grammar so a round-trip proves the output.
"""

from __future__ import annotations

import csv
import io
import json
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import quote

from apiforge.core.ids import stable_id

VERTICES_FILE = "vertices.csv"
EDGES_CSV_FILE = "edges.csv"
NTRIPLES_FILE = "graph.nt"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
_IRI = r"<[^<>\"{}|^`\\\s]+>"
_LITERAL = r'"(?:[^"\\\n\r]|\\[tbnrf"\'\\])*"'
_TRIPLE = re.compile(rf"^{_IRI} {_IRI} (?:{_IRI}|{_LITERAL}) \.$")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _cell(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def edge_id(edge: Mapping[str, Any]) -> str:
    return stable_id("edge", {"f": edge["from_id"], "t": edge["to_id"], "k": edge["kind"]})


def _csv(rows: list[list[str]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerows(rows)
    return buffer.getvalue()


def _prop_keys(items: Iterable[Mapping[str, Any]]) -> list[str]:
    return sorted({key for item in items for key in (item.get("props") or {})})


def gremlin_csv(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> tuple[str, str]:
    """(vertices.csv, edges.csv) text in Neptune's Gremlin load format."""
    node_keys = _prop_keys(nodes)
    vertex_rows = [["~id", "~label", *(f"{key}:String" for key in node_keys)]]
    for node in sorted(nodes, key=lambda n: n["id"]):
        props = node.get("props") or {}
        vertex_rows.append(
            [
                node["id"],
                node["kind"],
                *(_cell(props[key]) if key in props else "" for key in node_keys),
            ]
        )
    edge_keys = _prop_keys(edges)
    edge_rows = [["~id", "~from", "~to", "~label", *(f"{key}:String" for key in edge_keys)]]
    for edge in sorted(edges, key=edge_id):
        props = edge.get("props") or {}
        edge_rows.append(
            [
                edge_id(edge),
                edge["from_id"],
                edge["to_id"],
                edge["kind"],
                *(_cell(props[key]) if key in props else "" for key in edge_keys),
            ]
        )
    return _csv(vertex_rows), _csv(edge_rows)


def _iri(kind: str, value: str) -> str:
    return f"<urn:apiforge:{kind}:{quote(value, safe='-._~:')}>"


def _literal(value: Any) -> str:
    text = _cell(value)
    escaped = (
        text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
    )
    return f'"{escaped}"'


def ntriples(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
    """N-Triples text: node type, node properties and edges (edge props are not reified)."""
    lines: set[str] = set()
    for node in nodes:
        subject = _iri("node", node["id"])
        lines.add(f"{subject} <{RDF_TYPE}> {_iri('kind', node['kind'])} .")
        for key, value in (node.get("props") or {}).items():
            lines.add(f"{subject} {_iri('prop', key)} {_literal(value)} .")
    for edge in edges:
        lines.add(
            f"{_iri('node', edge['from_id'])} {_iri('edge', edge['kind'])} {_iri('node', edge['to_id'])} ."
        )
    return "".join(f"{line}\n" for line in sorted(lines))


def validate_gremlin_csv(vertices: str, edges: str) -> list[str]:
    """Loader-grammar errors; empty means the pair loads as written."""
    errors: list[str] = []
    vrows = list(csv.reader(io.StringIO(vertices)))
    erows = list(csv.reader(io.StringIO(edges)))
    if not vrows or vrows[0][:2] != ["~id", "~label"]:
        errors.append("vertices.csv header must start with ~id,~label")
    if not erows or erows[0][:4] != ["~id", "~from", "~to", "~label"]:
        errors.append("edges.csv header must start with ~id,~from,~to,~label")
    for name, rows, fixed in (("vertices.csv", vrows, 2), ("edges.csv", erows, 4)):
        for column in rows[0][fixed:] if rows else []:
            if not re.fullmatch(r"[^:~]+:String", column):
                errors.append(f"{name}: column {column!r} is not <name>:String")
        ids = [row[0] for row in rows[1:]]
        if any(not value for value in ids) or len(ids) != len(set(ids)):
            errors.append(f"{name}: ~id values must be present and unique")
        if any(len(row) != len(rows[0]) for row in rows[1:]):
            errors.append(f"{name}: every row needs {len(rows[0])} cells")
    known = {row[0] for row in vrows[1:]}
    for row in erows[1:]:
        if len(row) >= 3 and (row[1] not in known or row[2] not in known):
            errors.append(f"edges.csv: {row[0]} references a vertex that is not exported")
    return errors


def validate_ntriples(text: str) -> list[str]:
    """Line-level N-Triples 1.1 grammar errors (IRIs and plain literals)."""
    return [
        f"line {number}: not a valid triple"
        for number, line in enumerate(text.splitlines(), 1)
        if line.strip() and not _TRIPLE.match(line)
    ]
