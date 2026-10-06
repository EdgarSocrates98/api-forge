"""Inventory produced by the static FastAPI extractor."""

from __future__ import annotations

from apiforge.adapters.inventory import CodeInventory


class FastApiInventory(CodeInventory):
    """Every route fact, diagnostic and source hash found under a project root."""

    framework: str = "fastapi"
