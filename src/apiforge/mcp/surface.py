"""Measured MCP surface cost (§91): name, description and schema bytes per tool.

Schemas are derived from the tool signatures with pydantic — the same
information the SDK server publishes — so the surface can be measured without the
optional ``mcp`` extra. What a host actually loads (e.g. deferred tool
schemas) is host behavior, recorded in the host projection, not assumed here.
"""

from __future__ import annotations

import inspect
import json
import typing
from collections.abc import Callable
from typing import Any

from pydantic import create_model

from apiforge.contracts.base import ContractError
from apiforge.contracts.tool_host import ToolCost, ToolSurface


def tool_schema(fn: Callable[..., Any]) -> dict[str, Any]:
    hints = typing.get_type_hints(fn)
    fields: dict[str, Any] = {}
    for name, param in inspect.signature(fn).parameters.items():
        annotation = hints.get(name, Any)
        default = ... if param.default is inspect.Parameter.empty else param.default
        fields[name] = (annotation, default)
    schema: dict[str, Any] = create_model(f"{fn.__name__}_arguments", **fields).model_json_schema()
    return schema


def tool_cost(fn: Callable[..., Any]) -> ToolCost:
    doc = inspect.getdoc(fn) or ""
    schema = json.dumps(tool_schema(fn), sort_keys=True, separators=(",", ":"))
    return ToolCost(
        name=fn.__name__,
        name_bytes=len(fn.__name__.encode("utf-8")),
        description_bytes=len(doc.encode("utf-8")),
        schema_bytes=len(schema.encode("utf-8")),
    )


def surface_tools(surface: str) -> tuple[Callable[..., Any], ...]:
    from apiforge.mcp.gateway import GATEWAY_TOOLS, full_tools

    if surface == "full":
        return tuple(full_tools().values())
    if surface == "compact":
        return GATEWAY_TOOLS
    error = ContractError("AF-MCP-SURFACE-INVALID", f"surface {surface!r} is not full|compact")
    error.field = "surface"  # type: ignore[attr-defined]
    error.unlock = "pass --surface full or --surface compact"  # type: ignore[attr-defined]
    raise error


def measure_surface(surface: str = "full") -> ToolSurface:
    from apiforge.mcp.gateway import full_tools

    costs = tuple(tool_cost(fn) for fn in surface_tools(surface))
    total = sum(item.name_bytes + item.description_bytes + item.schema_bytes for item in costs)
    return ToolSurface(
        surface=surface,  # type: ignore[arg-type]
        tools=costs,
        tool_count=len(costs),
        total_bytes=total,
        reachable_capabilities=len(full_tools()),
    )


__all__ = ["measure_surface", "surface_tools", "tool_cost", "tool_schema"]
