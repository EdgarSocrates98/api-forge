"""Deterministic JUnit and Markdown projections for change-control runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from apiforge.contracts.change_control import ChangeControlResult


class ChangePublishError(ValueError):
    """A governed publisher refusal with a stable AF error code."""

    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        self.code = code
        self.detail = detail
        self.field = field
        self.unlock = unlock
        super().__init__(f"{code}: {detail} (field={field}; unlock={unlock})")


def _load_result(run_dir: Path) -> ChangeControlResult:
    result_path = run_dir / "result.json"
    if not result_path.is_file():
        raise ChangePublishError(
            "AF-CHANGE-PUBLISH-RESULT",
            str(result_path),
            field="run_dir/result.json",
            unlock="run `apiforge change-control run` before publishing",
        )
    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        return ChangeControlResult.model_validate(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ChangePublishError(
            "AF-CHANGE-PUBLISH-RESULT",
            str(exc),
            field="run_dir/result.json",
            unlock="regenerate the governed result and rerun the publisher",
        ) from exc


def _load_metrics(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "metrics.json"
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write(path: Path, content: str, *, code: str) -> str:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    except OSError as exc:
        raise ChangePublishError(
            code,
            str(exc),
            field=str(path),
            unlock="choose a writable local artifact path and retry",
        ) from exc
    return str(path)


def render_junit(result: ChangeControlResult, metrics: dict[str, Any] | None = None) -> str:
    """Render one governed decision as a CI-compatible JUnit document."""
    metrics = metrics or {}
    status = result.status
    suite = ET.Element(
        "testsuite",
        {
            "name": "api-forge-change-control",
            "tests": "1",
            "failures": "1" if status == "failed" else "0",
            "errors": "1" if status == "blocked" else "0",
            "skipped": "1" if status == "review" else "0",
            "time": str(
                sum(float(item.get("duration_ms", 0)) for item in metrics.get("stages", [])) / 1000
            ),
        },
    )
    case = ET.SubElement(
        suite,
        "testcase",
        {"classname": "apiforge.change_control", "name": "governed decision"},
    )
    if status == "review":
        ET.SubElement(case, "skipped", {"message": "human review is required"})
    elif status == "failed":
        failure = ET.SubElement(case, "failure", {"message": "change-control failed"})
        failure.text = "\n".join(result.gaps) or "change-control failed without a named gap"
    elif status == "blocked":
        error = ET.SubElement(case, "error", {"message": "change-control blocked"})
        error.text = "\n".join(result.gaps) or "change-control blocked without a named gap"
    output = ET.SubElement(case, "system-out")
    output.text = json.dumps(
        {
            "capability_id": result.capability_id,
            "state": result.state,
            "status": result.status,
            "evidence": list(result.evidence),
            "gaps": list(result.gaps),
            "limitations": list(result.limitations),
        },
        sort_keys=True,
    )
    ET.indent(suite, space="  ")
    return ET.tostring(suite, encoding="unicode", xml_declaration=True) + "\n"


def render_markdown(result: ChangeControlResult) -> str:
    """Render a reviewable, evidence-linked Markdown report."""
    payload = result.payload
    recommendation = payload.get("recommendation", {})
    if not isinstance(recommendation, dict):
        recommendation = {}
    lines = [
        "# API Forge change-control report",
        "",
        f"- Capability: `{result.capability_id}`",
        f"- State: `{result.state}`",
        f"- Status: `{result.status}`",
        "",
        "## Recommendation",
        "",
        str(recommendation.get("recommendation", "not available")),
        "",
        "| Field | Values |",
        "|---|---|",
    ]
    for field in (
        "facts",
        "assumptions",
        "alternatives",
        "risks",
        "unresolved",
        "evidence_refs",
        "verifier",
        "confidence",
    ):
        value = recommendation.get(field, ())
        rendered = (
            ", ".join(f"`{item}`" for item in value) if isinstance(value, list) else str(value)
        )
        lines.append(f"| `{field}` | {rendered or '—'} |")
    lines.extend(["", "## Gaps", ""])
    lines.extend(f"- {gap}" for gap in result.gaps) if result.gaps else lines.append("- None")
    lines.extend(["", "## Limitations", ""])
    lines.extend(
        f"- {item}" for item in result.limitations
    ) if result.limitations else lines.append("- None")
    lines.extend(["", "## Evidence", ""])
    lines.extend(f"- `{item}`" for item in result.evidence) if result.evidence else lines.append(
        "- None"
    )
    lines.append("")
    return "\n".join(lines)


def publish_change_control_reports(
    run_dir: Path,
    *,
    junit_path: Path | None = None,
    markdown_path: Path | None = None,
) -> dict[str, str]:
    """Write JUnit and Markdown projections from a canonical run result."""
    result = _load_result(run_dir)
    metrics = _load_metrics(run_dir)
    junit = junit_path or run_dir / "reports" / "change-control.junit.xml"
    markdown = markdown_path or run_dir / "reports" / "change-control.md"
    return {
        "junit": _write(junit, render_junit(result, metrics), code="AF-CHANGE-PUBLISH-JUNIT"),
        "markdown": _write(
            markdown,
            render_markdown(result),
            code="AF-CHANGE-PUBLISH-MARKDOWN",
        ),
    }
