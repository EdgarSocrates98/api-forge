from __future__ import annotations

from pathlib import Path

from scripts.sbom import build


def test_sbom_is_deterministic_and_hashed() -> None:
    root = Path(__file__).resolve().parents[2]
    first = build(root / "uv.lock")
    second = build(root / "uv.lock")
    assert first == second
    assert first["bomFormat"] == "CycloneDX"
    assert first["specVersion"] == "1.5"
    assert len(first["components"]) >= 60
    assert all("purl" in component for component in first["components"])
