from pathlib import Path

from apiforge.agentops.native import native_status


def test_native_vendor_status_is_complete() -> None:
    result = native_status(Path(__file__).parents[2])

    assert result["caveman"]["vendored"] is True  # type: ignore[index]
    assert result["cavekit"]["vendored"] is True  # type: ignore[index]
    assert result["rtk"]["config_present"] is True  # type: ignore[index]
    assert result["rtk"]["binary_embedded"] is False  # type: ignore[index]
    assert result["manifest"]["valid"] is True  # type: ignore[index]
