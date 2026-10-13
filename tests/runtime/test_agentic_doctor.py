"""`doctor --agentic` — cross-plane health stays honest about missing state."""

from pathlib import Path

from apiforge.runtime.agentic_doctor import diagnose_agentic


def test_empty_root_reports_unresolved(tmp_path: Path) -> None:
    report = diagnose_agentic(tmp_path)
    planes = {section.plane: section.state for section in report.sections}
    assert planes["case"] == "unresolved"
    assert planes["memory"] == "unresolved"
    assert planes["telemetry"] == "unresolved"
    assert planes["trust"] == "attention"  # packaged policy path missing under tmp root
    assert planes["mcp"] == "ok"  # registry is import-time, always observable
    assert report.unresolved
    assert report.status in {"attention", "unresolved"}


def test_repo_root_has_sections() -> None:
    report = diagnose_agentic(Path("."))
    planes = {section.plane for section in report.sections}
    assert planes == {
        "case",
        "memory",
        "trust",
        "telemetry",
        "evals",
        "sdd",
        "mcp",
        "economy",
    }
    mcp = next(s for s in report.sections if s.plane == "mcp")
    assert any(c.startswith("tools-declared:") for c in mcp.checks)
