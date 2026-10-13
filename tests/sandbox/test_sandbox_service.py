import json
from pathlib import Path

from apiforge.sandbox.service import sandbox_apply, sandbox_clean
from tests.sandbox.diffs import (
    DIFF_ADDING_ROUTE,
    DIFF_BINARY,
    DIFF_MISSING_TARGET,
    DIFF_MODE_ONLY,
    DIFF_TOUCHING_EVIL,
)


def test_diff_path_outside_copy_is_refused(sandbox_project: Path, analyze_stub) -> None:
    report = sandbox_apply(sandbox_project, DIFF_TOUCHING_EVIL, analyze_stub)
    assert report["applied"] is False
    assert report["refused"][0]["code"] == "AF-SANDBOX-PATH-OUTSIDE"


def test_binary_diff_is_refused(sandbox_project: Path, analyze_stub) -> None:
    report = sandbox_apply(sandbox_project, DIFF_BINARY, analyze_stub)
    assert report["applied"] is False
    assert report["refused"][0]["code"] == "AF-SANDBOX-BINARY-PATCH"


def test_mode_only_is_refused(sandbox_project: Path, analyze_stub) -> None:
    report = sandbox_apply(sandbox_project, DIFF_MODE_ONLY, analyze_stub)
    assert report["refused"][0]["code"] == "AF-SANDBOX-MODE-ONLY"


def test_missing_target_is_refused(sandbox_project: Path, analyze_stub) -> None:
    report = sandbox_apply(sandbox_project, DIFF_MISSING_TARGET, analyze_stub)
    assert report["refused"][0]["code"] == "AF-SANDBOX-TARGET-MISSING"


def test_sandbox_reports_finding_delta(sandbox_project: Path, analyze) -> None:
    report = sandbox_apply(sandbox_project, DIFF_ADDING_ROUTE, analyze)
    assert report["applied"] is True
    assert report["main_tree_touched"] is False
    assert any(f["path"] == "/orders/extra" for f in report["new"])
    assert report["kept_count"] > 0
    assert (
        not (sandbox_project / "app" / "routes" / "orders.py")
        .read_text(encoding="utf-8")
        .endswith("extra")
    )


def test_same_diff_same_id(sandbox_project: Path, analyze) -> None:
    first = sandbox_apply(sandbox_project, DIFF_ADDING_ROUTE, analyze)
    second = sandbox_apply(sandbox_project, DIFF_ADDING_ROUTE, analyze)
    assert first["id"] == second["id"]
    assert (sandbox_project / ".apiforge" / "sandbox" / first["id"]).is_dir()


def test_report_file_written(sandbox_project: Path, analyze) -> None:
    report = sandbox_apply(sandbox_project, DIFF_ADDING_ROUTE, analyze)
    report_file = sandbox_project / ".apiforge" / "sandbox" / report["id"] / "report.json"
    assert json.loads(report_file.read_text(encoding="utf-8"))["id"] == report["id"]


def test_clean_removes_only_sandbox_dir(sandbox_project: Path, analyze) -> None:
    report = sandbox_apply(sandbox_project, DIFF_ADDING_ROUTE, analyze)
    result = sandbox_clean(sandbox_project)
    assert report["id"] in result["removed"]
    assert not (sandbox_project / ".apiforge" / "sandbox").exists()
    assert (sandbox_project / "app").is_dir()
