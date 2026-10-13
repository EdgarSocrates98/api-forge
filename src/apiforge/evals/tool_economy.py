"""Tool/host economy eval (wave 5): cheaper projections, same evidence.

Case kinds:

- ``output``: real payloads from an analyzed fixture; compact must be
  ≤ ``max_ratio`` of the json bytes and lossless (``loads(compact) == prune(json)``);
- ``tests`` / ``log``: slicers must find every expected failure/signature and
  stay ≤ 20% of the log bytes for logs ≥ 4 KB;
- ``discover``: the expected tool is in the top 5 of ``apiforge_discover``.

Suite-level gates: compact MCP surface ≤ 25% of the full surface bytes and
every full tool reachable through ``apiforge_call``.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError

_IGNORED = shutil.ignore_patterns(".apiforge", "__pycache__", "*.pyc", "conftest.py")
SLICE_RATIO = 0.2
SURFACE_RATIO = 0.25


def load_corpus(corpus: Path) -> list[dict[str, Any]]:
    rows = [
        yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [str(row.get("id")) for row in rows]
    if not rows or len(set(ids)) != len(ids):
        raise ContractError("AF-EVALS-INVALID", f"tool-economy corpus {corpus} empty or duplicated")
    return rows


def _output(row: dict[str, Any], repo_root: Path, workdir: Path) -> dict[str, Any]:
    from apiforge.agentops.agent_audit import audit_agents
    from apiforge.application.analyze import analyze_project
    from apiforge.application.cache import cache_stats, context_delta
    from apiforge.application.context import build_context_capsule
    from apiforge.economy.run_ledger import stats
    from apiforge.knowledge.selector import select_expertise
    from apiforge.mcp.surface import measure_surface
    from apiforge.output.render import prune, render

    root = workdir / str(row["id"])
    shutil.copytree(repo_root / str(row["fixture"]), root / "proj", ignore=_IGNORED)
    shutil.copyfile(repo_root / str(row["contract"]), root / "openapi.yaml")
    analyze_project(root / "openapi.yaml", root / "proj", None, root / ".apiforge" / "case")
    payloads: dict[str, Any] = {
        "context capsule": build_context_capsule(root, target=str(row["target"])),
        "economy stats": stats(root),
        "cache stats": cache_stats(root),
        "context delta": context_delta(root, changed=("proj/app/models.py",)),
        "knowledge select": select_expertise("make POST /payments idempotent").model_dump(
            mode="json"
        ),
        "agents audit": audit_agents(repo_root),
        "mcp surface": measure_surface("compact").model_dump(mode="json"),
    }
    items = []
    for name, value in payloads.items():
        full = render(value, "json")
        compact = render(value, "compact")
        items.append(
            {
                "payload": name,
                "json_bytes": len(full.encode("utf-8")),
                "compact_bytes": len(compact.encode("utf-8")),
                "lossless": json.loads(compact) == prune(json.loads(full)),
            }
        )
    total_json = sum(item["json_bytes"] for item in items)
    total_compact = sum(item["compact_bytes"] for item in items)
    ratio = round(total_compact / total_json, 4) if total_json else 1.0
    return {
        "case_id": row["id"],
        "kind": "output",
        "payloads": items,
        "ratio": ratio,
        "passed": ratio <= float(row.get("max_ratio", 0.6)) and all(i["lossless"] for i in items),
    }


def _slice(row: dict[str, Any], corpus: Path, workdir: Path) -> dict[str, Any]:
    from apiforge.agentops.slicing import slice_log, slice_tests

    path = corpus / str(row["input"])
    if row["kind"] == "tests":
        result = slice_tests(workdir, path, str(row.get("format", "auto")))
        found = {item.test for item in result.failures}
        expected = set(row.get("expect_failed") or ())
        counts = {k: getattr(result, k) for k in (row.get("expect_counts") or {})}
        recall_ok = expected <= found and counts == dict(row.get("expect_counts") or {})
        detail: dict[str, Any] = {"failures": sorted(found), "counts": counts}
    else:
        log = slice_log(workdir, path)
        lines = [item.first_line for item in log.signatures]
        wanted = list(row.get("expect_signatures") or ())
        recall_ok = all(any(term in line for line in lines) for term in wanted)
        for term, count in (row.get("expect_count") or {}).items():
            recall_ok = recall_ok and any(
                term in item.first_line and item.count == int(count) for item in log.signatures
            )
        detail = {
            "signatures": [f"{item.count}x {item.first_line[:80]}" for item in log.signatures]
        }
        result = log  # type: ignore[assignment]
    ratio = round(result.slice_bytes / result.original_bytes, 4) if result.original_bytes else 1.0
    small = result.original_bytes < 4096
    return {
        "case_id": row["id"],
        "kind": row["kind"],
        "original_bytes": result.original_bytes,
        "slice_bytes": result.slice_bytes,
        "ratio": ratio,
        **detail,
        "passed": recall_ok and (small or ratio <= SLICE_RATIO),
    }


def _discover(row: dict[str, Any]) -> dict[str, Any]:
    from apiforge.mcp.gateway import apiforge_discover

    matches = [item["tool"] for item in apiforge_discover(str(row["query"]), 5)["matches"]]
    return {
        "case_id": row["id"],
        "kind": "discover",
        "top5": matches,
        "passed": str(row["expect_tool"]) in matches,
    }


def run_tool_economy(corpus: Path, repo_root: Path) -> dict[str, Any]:
    from apiforge.mcp.gateway import full_tools
    from apiforge.mcp.surface import measure_surface
    from apiforge.mcp.tools import GRPC_TOOLS, MIGRATION_TOOLS, OBSERVABILITY_TOOLS, TOOLS

    rows_in = load_corpus(Path(corpus))
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-tool-economy-") as tmp:
        for row in rows_in:
            if row["kind"] == "output":
                rows.append(_output(row, Path(repo_root), Path(tmp)))
            elif row["kind"] in {"tests", "log"}:
                rows.append(_slice(row, Path(corpus), Path(tmp)))
            else:
                rows.append(_discover(row))
    full = measure_surface("full")
    compact = measure_surface("compact")
    registered = {
        fn.__name__ for fn in (*TOOLS, *OBSERVABILITY_TOOLS, *GRPC_TOOLS, *MIGRATION_TOOLS)
    }
    reachable = set(full_tools())
    surface_ratio = round(compact.total_bytes / full.total_bytes, 4) if full.total_bytes else 1.0
    gates = {
        "compact_output": all(r["passed"] for r in rows if r["kind"] == "output"),
        "slicer_recall_and_size": all(r["passed"] for r in rows if r["kind"] in {"tests", "log"}),
        "discover_top5": all(r["passed"] for r in rows if r["kind"] == "discover"),
        "compact_surface": surface_ratio <= SURFACE_RATIO,
        "capability_reachable": registered == reachable,
    }
    return {
        "schema": "apiforge/tool-economy-eval/v1",
        "cases": len(rows),
        "surface": {
            "full_tools": full.tool_count,
            "full_bytes": full.total_bytes,
            "compact_tools": compact.tool_count,
            "compact_bytes": compact.total_bytes,
            "ratio": surface_ratio,
            "reachable": len(reachable),
        },
        "gates": gates,
        "passed": all(gates.values()),
        "rows": rows,
        "tokens": "unresolved",
    }


__all__ = ["load_corpus", "run_tool_economy"]
