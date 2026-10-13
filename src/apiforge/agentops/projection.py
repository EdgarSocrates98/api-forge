"""Host projections (§92–93): declared host behavior → economical projection."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.tool_host import HostProjection

PROJECTION_FILE = Path(__file__).resolve().parents[1] / "rules" / "host_projections.yaml"


@lru_cache(maxsize=2)
def load_projections(path: Path = PROJECTION_FILE) -> dict[str, Any]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ContractError("AF-HOST-PROJECTION-INVALID", f"{path}: {exc}") from exc
    if raw.get("schema") != "apiforge/host-projections/v1" or not isinstance(
        raw.get("hosts"), dict
    ):
        raise ContractError("AF-HOST-PROJECTION-INVALID", f"{path}: missing schema or hosts")
    return raw


def project_host(host: str) -> HostProjection:
    from apiforge.mcp.surface import measure_surface

    table = load_projections()
    row = table["hosts"].get(host)
    if row is None:
        error = ContractError("AF-HOST-UNKNOWN", f"host {host!r} is not declared")
        error.field = "host"  # type: ignore[attr-defined]
        error.unlock = f"use one of {sorted(table['hosts'])}"  # type: ignore[attr-defined]
        raise error
    surface = str(row.get("mcp_surface", "full"))
    return HostProjection(
        host=host,
        instruction_file=str(row.get("instruction_file", "")),
        mcp_surface=surface,  # type: ignore[arg-type]
        output=str(row.get("output", "json")),  # type: ignore[arg-type]
        deferred_tools=bool(row.get("deferred_tools", False)),
        surface_bytes=measure_surface(surface).total_bytes,
        full_surface_bytes=measure_surface("full").total_bytes,
        verb_map={str(k): str(v) for k, v in (table.get("verb_map") or {}).items()},
        notes=tuple(str(item) for item in row.get("notes") or ()),
    )


__all__ = ["PROJECTION_FILE", "load_projections", "project_host"]
