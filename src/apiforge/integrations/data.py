"""Database integration contract for static access-pattern evidence."""

from apiforge.capabilities.registry import load_capabilities
from apiforge.integrations.gateway import StaticIntegrationAdapter


def local_data_adapter() -> StaticIntegrationAdapter:
    records = tuple(item for item in load_capabilities() if item.vertical == "database")
    return StaticIntegrationAdapter("data", records)
