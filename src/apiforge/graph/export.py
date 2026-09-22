"""Export the canonical graph — byte-identical copy plus a digest manifest."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.graph import GraphExport
from apiforge.graph.store import EDGES_FILE, NODES_FILE


def export_graph(graph_dir: Path, out_dir: Path, fmt: str = "jsonl") -> GraphExport:
    """Copy nodes/edges canonically and emit `export.json` with digests.

    `neptune` is a named stub: the OpenCSV layout is planned but not
    implemented -- requesting it refuses loudly instead of emitting a
    half-mapped file.
    """
    if fmt != "jsonl":
        raise ContractError(
            "AF-GRAPH-FORMAT",
            f"format {fmt!r} is named but not implemented; only 'jsonl' exports",
        )
    src = Path(graph_dir)
    nodes = src / NODES_FILE
    if not nodes.is_file():
        raise ContractError("AF-GRAPH-NOT-FOUND", f"no {NODES_FILE} under {src}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name in (NODES_FILE, EDGES_FILE):
        target = src / name
        if target.is_file():
            shutil.copyfile(target, out / name)
    export = GraphExport(
        nodes_sha256=hashlib.sha256(nodes.read_bytes()).hexdigest(),
        edges_sha256=hashlib.sha256((src / EDGES_FILE).read_bytes()).hexdigest()
        if (src / EDGES_FILE).is_file()
        else "0" * 64,
        node_count=sum(
            1 for line in nodes.read_text(encoding="utf-8").splitlines() if line.strip()
        ),
        edge_count=sum(
            1
            for line in (src / EDGES_FILE).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        if (src / EDGES_FILE).is_file()
        else 0,
        built_from=(),
        format="jsonl",
    )
    import json

    (out / "export.json").write_text(
        json.dumps(export.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return export


def export_summary(export: GraphExport) -> dict[str, Any]:
    return export.model_dump(mode="json")
