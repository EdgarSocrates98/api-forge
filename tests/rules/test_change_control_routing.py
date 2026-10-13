from __future__ import annotations

from apiforge.application.next_step import load_routing


def test_contract_discovery_has_a_governance_route() -> None:
    assert any(
        route.phase == "discover" and route.dominant_area == "CONTRACT" for route in load_routing()
    )
