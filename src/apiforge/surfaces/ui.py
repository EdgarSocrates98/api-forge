"""Framework-neutral UI projection over canonical platform results."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from apiforge.capabilities.registry import load_capabilities
from apiforge.contracts.platform import CapabilityRequest
from apiforge.surfaces.projection import project_capability


def handle(request: Mapping[str, Any]) -> dict[str, object]:
    """Return data for a visual host; mutation remains policy-gated."""
    parsed = CapabilityRequest.model_validate(request)
    return project_capability(parsed, load_capabilities()).model_dump(mode="json")
