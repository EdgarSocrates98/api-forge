"""Export the canonical graph — jsonl copy, Neptune Gremlin CSV or RDF N-Triples.

Every format writes `export.json` with the source digests and the digest
of each written file. Projections are re-validated against their loader
grammar before `export.json` is written; an invalid projection refuses.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.graph import GraphExport
from apiforge.graph import formats
from apiforge.graph.store import EDGES_FILE, NODES_FILE

FORMATS = ("jsonl", "neptune", "rdf")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(out: Path, name: str, text: str) -> Path:
    target = out / name
    target.write_bytes(text.encode("utf-8"))
    return target


def export_graph(graph_dir: Path, out_dir: Path, fmt: str = "jsonl") -> GraphExport:
    """Write the requested projection and `export.json` with digests."""
    if fmt not in FORMATS:
        raise ContractError(
            "AF-GRAPH-FORMAT",
            f"format {fmt!r} is not implemented; use one of {', '.join(FORMATS)}",
        )
    src = Path(graph_dir)
    nodes_path = src / NODES_FILE
    edges_path = src / EDGES_FILE
    if not nodes_path.is_file():
        raise ContractError("AF-GRAPH-NOT-FOUND", f"no {NODES_FILE} under {src}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    nodes = formats.read_jsonl(nodes_path)
    edges = formats.read_jsonl(edges_path)
    written: list[Path] = []
    if fmt == "jsonl":
        for name in (NODES_FILE, EDGES_FILE):
            if (src / name).is_file():
                shutil.copyfile(src / name, out / name)
                written.append(out / name)
    elif fmt == "neptune":
        vertices, edge_rows = formats.gremlin_csv(nodes, edges)
        errors = formats.validate_gremlin_csv(vertices, edge_rows)
        if errors:
            raise ContractError("AF-GRAPH-EXPORT-INVALID", "; ".join(errors))
        written.append(_write(out, formats.VERTICES_FILE, vertices))
        written.append(_write(out, formats.EDGES_CSV_FILE, edge_rows))
    else:
        triples = formats.ntriples(nodes, edges)
        errors = formats.validate_ntriples(triples)
        if errors:
            raise ContractError("AF-GRAPH-EXPORT-INVALID", "; ".join(errors[:5]))
        written.append(_write(out, formats.NTRIPLES_FILE, triples))
    export = GraphExport(
        nodes_sha256=_sha(nodes_path),
        edges_sha256=_sha(edges_path) if edges_path.is_file() else "0" * 64,
        node_count=len(nodes),
        edge_count=len(edges),
        built_from=(),
        format=fmt,  # type: ignore[arg-type]
        files=tuple(sorted((path.name, _sha(path)) for path in written)),
    )
    (out / "export.json").write_text(
        json.dumps(export.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return export


def export_summary(export: GraphExport) -> dict[str, Any]:
    return export.model_dump(mode="json")
