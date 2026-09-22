from __future__ import annotations

from pathlib import Path

from apiforge.application.platform import ApiForgePlatform


def test_platform_facade_discovery_exposes_execution_provenance() -> None:
    result = ApiForgePlatform(Path.cwd()).discover(Path("tests/fixtures/fastapi_orders"))
    assert result["framework"] == "fastapi"
    assert result["execution"]["mode"] == "static"
    assert result["execution"]["evidence_level"] in {"heuristic", "unknown"}
