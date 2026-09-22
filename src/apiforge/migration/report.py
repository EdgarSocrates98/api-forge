"""Human-readable migration report rendering."""

from __future__ import annotations

import json

from apiforge.migration.contracts import MigrationReport


def render_report(report: MigrationReport, *, markdown: bool = False) -> str:
    payload = report.model_dump(mode="json")
    if not markdown:
        return json.dumps(payload, indent=2, sort_keys=True)
    status = report.outcome.status.value if report.outcome else "REVIEW"
    lines = [
        f"# Runtime migration: {status}",
        "",
        f"- Identity: `{report.spec_identity}`",
        f"- Files: {len(report.discovery.detected_files)}",
        f"- Findings: {len(report.plan.findings)}",
        "",
        "## Gaps",
    ]
    if report.gaps:
        lines.extend(f"- {gap}" for gap in report.gaps)
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"
