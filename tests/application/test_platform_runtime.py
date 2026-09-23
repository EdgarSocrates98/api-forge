from __future__ import annotations

from pathlib import Path

from apiforge.application.platform_runtime import runtime_summary, verify_platform_runtime


def test_all_platform_vertical_probes_execute_and_emit_receipt() -> None:
    receipt = verify_platform_runtime(
        Path("."),
        now="2026-09-22T12:00:00+00:00",
    )
    assert receipt.schema_version == "af-platform-runtime-receipt/1"
    assert runtime_summary(receipt)["ok"] is True
    assert {item.vertical for item in receipt.verticals} == {
        "api",
        "database",
        "messaging",
        "cicd",
        "cloud",
        "frontend",
    }
    assert all(item.status == "passed" for item in receipt.verticals)
