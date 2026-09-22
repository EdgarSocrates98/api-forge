"""Cloud integration contract for declared IaC and posture artifacts."""

from apiforge.capabilities.registry import load_capabilities
from apiforge.integrations.gateway import StaticIntegrationAdapter


def local_cloud_adapter() -> StaticIntegrationAdapter:
    records = tuple(item for item in load_capabilities() if item.vertical == "cloud")
    return StaticIntegrationAdapter("cloud", records)
