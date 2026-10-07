from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "tests" / "labs" / "platform_verticals.yaml"
EXPECTED = {"api", "database", "messaging", "cicd", "cloud", "frontend"}


def _verticals() -> dict[str, dict[str, str]]:
    document = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    return dict(document["verticals"])


def test_vertical_coverage() -> None:
    verticals = _verticals()
    assert set(verticals) == EXPECTED
    for vertical, cell in verticals.items():
        fixture = ROOT / cell["fixture"]
        golden = ROOT / cell["golden"]
        holdout = ROOT / cell["holdout"]
        assert fixture.is_dir(), vertical
        assert golden.is_file(), vertical
        assert holdout.is_file(), vertical
        assert json.loads(golden.read_text(encoding="utf-8"))["vertical"] == vertical
        holdout_doc = yaml.safe_load(holdout.read_text(encoding="utf-8"))
        assert holdout_doc["status"] in {"unresolved", "unsupported", "inconclusive"}
