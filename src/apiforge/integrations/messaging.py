"""Messaging integration contract for declared topology and source evidence."""

from apiforge.capabilities.registry import load_capabilities
from apiforge.integrations.gateway import StaticIntegrationAdapter


def local_messaging_adapter() -> StaticIntegrationAdapter:
    records = tuple(item for item in load_capabilities() if item.vertical == "messaging")
    return StaticIntegrationAdapter("messaging", records)
