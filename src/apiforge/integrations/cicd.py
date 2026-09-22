"""CI/CD integration contract for read-only pipeline and report inspection."""

from __future__ import annotations

from apiforge.capabilities.registry import load_capabilities
from apiforge.integrations.gateway import StaticIntegrationAdapter


def local_cicd_adapter() -> StaticIntegrationAdapter:
    records = tuple(item for item in load_capabilities() if item.vertical == "cicd")
    return StaticIntegrationAdapter("cicd", records)
